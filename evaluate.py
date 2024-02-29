def evaluate(code_arr: list[str], input, output):
  code = ""
  for line in code_arr:
    code += line + "\n"
  loc = {}

  exec(code, {'input': input, 'output': output}, loc)
  return loc['return_val']
  
if __name__ == '__main__':
  # example test
  print(
    evaluate(
      [
        "if output['#'] == 0:",
        "  return_val = output['RSRP(dBm)']",
        "else:",
        "  return_val = None"
      ], 
      {}, # input packet, if needed
      {'RSRP(dBm)': 'xabc', '#': 0} # _obj
    )
  )