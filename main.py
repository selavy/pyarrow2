import wrapt
import pyarrow as pa
import numpy as np
import pandas as pd

import pyarrow.compute as pc
import pyarrow.acero as pac


rng = np.random.default_rng(seed=42)


n = 10
df = pd.DataFrame(data={
    "x": rng.random(n),
    "y": rng.random(n),
    "z": rng.random(n),
})
print(df)


class MyTable(wrapt.ObjectProxy):
    def __setitem__(self, key, value):
        table = self.__wrapped__
        print(f"setitem({key}) = {value!r}: {table.column_names!r}")
        decl = pac.Declaration.from_sequence([
            pac.Declaration("table_source", pac.TableSourceNodeOptions(table)),
            pac.Declaration("project", pac.ProjectNodeOptions([value], [key])),
        ])
        self.__wrapped__ = table.append_column(key, decl.to_table()[key])

    def __call__(self, key):
        if key not in self.__wrapped__.column_names:
            raise KeyError(f"Invalid column: {key!r}. Have {self.__wrapped__.column_names!r}")
        return pc.field(key)


table = pa.Table.from_pandas(df)

print(f'XXX: {table["x"]}')

t2 = MyTable(table)
t2["a"] = pc.field("x") + pc.field("y")
print(t2)
t2["b"] = t2("a") * t2("x")
print(t2)

x2 = t2("x") + t2("x")
x4 = x2 + x2
t2["x4_v1"] = x4
t2["x4_v2"] = t2("x") * 4
print(t2)


# expr = pc.field("x") + pc.field("y")
#
# t2["a"] = expr
#
# print(expr)
#
# projection_a = pac.ProjectNodeOptions([expr], ["a"])
#
# decl = pac.Declaration.from_sequence([
#     pac.Declaration("table_source", pac.TableSourceNodeOptions(table)),
#     pac.Declaration("project", projection_a),
# ])
#
# result = decl.to_table()
# print(result)
#
#
# # decl = pac.Declaration.from_sequence([
# #     table,
# #     pac.ProjectNodeOptions(
# #         expressions=[
# #             expr,
# #             # pc.field("x") + pc.field("y"),
# #             # pc.field("x") * 2,
# #         ],
# #         names=[
# #             # "z",
# #             "x2",
# #         ],
# #     )
# # ])
# # print("HERE")
# # print(decl)
# # print("HERE2")
# # result = decl.to_table()
# # print(result)
