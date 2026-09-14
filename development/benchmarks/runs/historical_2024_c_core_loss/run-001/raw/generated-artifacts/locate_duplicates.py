import openpyxl, hashlib, collections

p = r'C:\Users\aaa\Desktop\text\pressure-test\附件一（训练集）.xlsx'
wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
for ws in wb.worksheets:
    d = collections.defaultdict(list)
    for r, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        h = hashlib.sha1(repr(tuple(row[:1028])).encode('utf-8')).hexdigest()
        d[h].append(r)
    dup = [rows for rows in d.values() if len(rows) > 1]
    print(ws.title, dup[:10])
