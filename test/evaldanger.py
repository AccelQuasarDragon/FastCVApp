#https://stackoverflow.com/questions/70862189/how-to-create-variable-names-dynamically-and-assigning-values-in-python
# example fails
# wutguy = f'{"".join(["stri", i])}=1'
# wutguy = f'=1'
# wutguy = {"".join(["stri", "1"])}
# print(wutguy)

# stri = "mat"

# for i in range(1,2):  
#     eval(f'{"".join([stri, str(i)])} = 1')

stri = "mat"

# exec("mat_1 = str(1)")

for i in range(1,2):  
    exec(f'{"_".join([stri, str(i)])}=1')
print(mat_1)
