import datetime

def solve(script):
    variables = {}
    va = script.split("{")[3]
    for v in va.split(";"):
        if v.startswith("var ") and "=" in v and v.split("=")[1].isdigit() and len(v.split("=")) == 2:
            variables[v.split("=")[0].replace("var ","")] = int(v.split("=")[1])
    script = script.split(f"var {list(variables.keys())[-1]}={list(variables.values())[-1]};")[1]
    current_line = 0
    while True:
        var_calc = False
        function = False
        if script.split(";")[current_line].startswith("return {'rf':"):
            break
        for vn in list(variables.keys()):
            if script.split(";")[current_line].startswith(f"{vn}=~"):
                var_calc = True
                break
            for operand in ["^","*","&","|"]:
                if script.split(";")[current_line].startswith(f"{vn}={vn}{operand}"):
                    var_calc = True
                    break
            if script.split(";")[current_line].startswith(f"{vn}=function("):
                function = True
            if var_calc or function:
                break
        if var_calc:
            expr = script.split(";")[current_line]
            if "new " not in expr:
                for vn in list(variables.keys()):
                    expr = expr.replace(vn, f"variables['{vn}']")
                exec(expr)
            elif "new " in expr:
                for vn in list(variables.keys()):
                    expr = expr.replace(vn, f"variables['{vn}']")
                date_arg = expr.split("new Date(")[1].split(")")[0]
                if variables[date_arg.split("variables['")[1].split("'")[0]] < 0:
                    date_arg2 = f"(datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=(({date_arg})/1000))).day"
                else:
                    date_arg2 = f'datetime.datetime.fromtimestamp(({date_arg})/1000, datetime.timezone.utc).day'
                expr = expr.replace(f"new Date({date_arg}).getUTCDate()", date_arg2)
                exec(expr)
            current_line += 1
            continue
        if function:
            func_first_arg = script.split(";")[current_line].split("=")[0]
            func_body = ""
            for l in script.split(";")[current_line:]:
                func_body += (l + ";")
                if l.startswith(f"}}({func_first_arg}"):
                    break
            if "document." not in func_body:
                args = func_body.split("(")[-1].split(")")[0].split(",")
                sub_func = lambda n: variables[args[2]] ^ n
                variables[func_first_arg] = sub_func(variables[args[0]]) | sub_func(variables[args[1]])
            elif "document." in func_body:
                args = func_body.split("(")[-1].split(")")[0].split(",")
                div1 = []
                def sub_func_1(div, n2):
                    for i in range(8):
                        div += [[n2]]
                        if (n2 & 1) == 0:
                            div = [[div], n2]
                        n2 = n2 >> 1
                    return div
                def sub_func_2(div, div2, n):
                    div = [int("".join([ch for ch in n if ch.isdigit() or ch == "-"])) for n in [n for n in str(div).split(",")[::-1] if "[" not in n]]
                    if sum(div) < 0:
                      return -((-sum(div)) % 256)
                    return sum(div) % 256
                variables[func_first_arg] = sub_func_2(sub_func_1(sub_func_1(sub_func_1(div1, variables[args[0]]), variables[args[1]]), variables[args[2]]), div1, 0)
            current_line += func_body.count(";") - 1
        current_line += 1
    return {
        "rf": variables,
        "s": script.split(";")[current_line].split("},'s':'")[1].split("'")[0]
    }
