def evaluate(code_arr: list[str], mapped_data):
    code = "\n".join(code_arr)
    print(code)
    namespace = {'_obj': mapped_data}  # Create a namespace where _obj references mapped_data
    print(namespace)
    exec(code, namespace)
    return namespace.get('return_val')
