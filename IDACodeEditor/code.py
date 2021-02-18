import idc
start = 0x4013a6
end = 0x4013d7

result = []

while (start <= end):
    result.append(idc.get_operand_value(start, 1))
    start = idc.next_head(start)

print(["0x%02X" % x for x in result])

