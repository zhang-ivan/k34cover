def assign_diagonal(cover, order_):  # Input a sorted cover!
    assigned_dict = {}
    l_ = len(cover)
    occurrence_ = []
    for i in range(1, order_ + 1):
        occurrence_.append([i])
        for j in range(l_):
            if i in cover[j]:
                occurrence_[i - 1].append(cover[j])
    while len(occurrence_) > 0:
        occurrence_ = sorted(occurrence_, key=lambda x: len(x))
        i_ = occurrence_[0][0]
        assigned_dict[i_] = occurrence_[0][1]
        for row in occurrence_:
            try:
                row.remove(assigned_dict[i_])
            except ValueError:
                pass
        del occurrence_[0]
    assigned_dict = dict(sorted(assigned_dict.items()))
    return assigned_dict