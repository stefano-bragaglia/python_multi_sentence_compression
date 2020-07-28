"""
MATCH (il5:Gene{desc:'IL5'})-[r]-(n)
WHERE NOT type(r) IN ['HAS_LINK', 'CO_OCCURS']
RETURN DISTINCT type(r), count(r) AS occur ORDER BY occur DESC

"""



