def tree_edit_distance(t1: dict, t2: dict, depth=0) -> int:
    # Limit depth to prevent recursion errors on massive DOMs
    if depth > 50:
        return 0
    
    # Compare tags (handle missing tags safely)
    tag1 = t1.get("tag", "").upper()
    tag2 = t2.get("tag", "").upper()
    cost = 1 if tag1 != tag2 else 0
    
    c1 = t1.get("children", [])
    c2 = t2.get("children", [])
    
    # Base structural difference
    total = abs(len(c1) - len(c2))
    
    # Compare common children
    for child1, child2 in zip(c1, c2):
        if isinstance(child1, dict) and isinstance(child2, dict):
            total += tree_edit_distance(child1, child2, depth + 1)
        else:
            total += 1
            
    return cost + total