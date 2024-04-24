from Model.feeding_site import Site

site1 = Site((0, 0), 5, 1, 1)
site2 = Site((1, 0), 2, 2, 2)
site3 = Site((2, 0), 1, 1, 1)

sites = [site1, site2, site3]
memory = [site1, site2, site3]

viable_sites = list(filter(lambda i: i not in memory, sites))
if len(viable_sites) > 0:
    print(f"Viable site found: {viable_sites}")
else:
    print("No viable site found")