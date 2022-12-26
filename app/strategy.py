def calc_diff(data_list):
    
    diff = ((data_list[0]['close'] / data_list[1]['close']) - 1) * 100
    
    return diff
    