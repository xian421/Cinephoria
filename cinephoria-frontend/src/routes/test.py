
existing_seats = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']
new_seats = ['A1', 'A2', 'A3', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

existing_set = set(existing_seats)
new_set = set(new_seats)

print('existing', existing_set)
print(new_set)
to_add = new_set - existing_set  # Sitzplätze, die hinzugefügt werden müssen
to_remove = existing_set - new_set  # Sitzplätze, die gelöscht werden müssen
print(to_add)
print(to_remove)

for seat in to_add:
    print('add', seat)