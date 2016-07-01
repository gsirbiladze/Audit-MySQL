    

def print_table(table, col_sep='|', rec_sep='-', intersect_char='+', hf_char='=', jright=False, first_is_header=False,  separate_recs=True, print_summary=False):
    """
    ===================================================================================================================

            table   : Two dimentional array(list)

            col_sep : Column separator character, default value '|'

            rec_sep : Records(lines) separator character, default value '-'

     intersect_char : Intersect(corners) character, default value  '+'

            hf_char : Character for header and footer, default value '='
    -------------------------------------------------------------------------------------------------------------------

             jright : Records alignment, default value 'False'(means all are left aligned)

    first_is_header : Declaring that the first record is a column title, default value 'False'

      separate_recs : Draw lines in between the records, default value 'True'

      print_summary : Print summary, default value 'False'

    ===================================================================================================================
    """

    #analyze table 
    rec_count      = len(table)
    max_row_count  = max([len(cols) for cols in table])
    col_max_len    = [0 for i in range(max_row_count)]
    sumarry        = 'Rec = {0}, Columns = {1} '.format(rec_count, len(col_max_len))
    # To fit summary in case first column's max length is shorter
    col_max_len[0] =  len(sumarry) if len(sumarry) > col_max_len[0] else col_max_len[0]
    
    

    for rec_id in range(rec_count):
        # make row even to all records
        for i in range(len(table[rec_id]), max_row_count):
            table[rec_id].append('')
    
        for i in range(max_row_count):
            table[rec_id][i] = str(table[rec_id][i]).replace('\n','')
            col_max_len[i] = len(table[rec_id][i]) if len(table[rec_id][i]) >  col_max_len[i] else col_max_len[i]
        
    
    row_delimiter = ''
    for f_len in col_max_len:
        row_delimiter = row_delimiter + intersect_char + ''.rjust(f_len,rec_sep)
    row_delimiter = row_delimiter + intersect_char
    
    
    header_footer = intersect_char + ''.rjust(len(row_delimiter)-2, hf_char) + intersect_char
    
    for rec_id in range(rec_count):
        rec_line_str = ''
        if rec_id == 0:
            print(header_footer)
        elif rec_id == 1 and first_is_header:
            print(header_footer)
        elif separate_recs:
            print(row_delimiter)
    
        for col_id in range(max_row_count):
             rec_str = table[rec_id][col_id].rjust(col_max_len[col_id]) if jright else table[rec_id][col_id].ljust(col_max_len[col_id])
             rec_line_str = rec_line_str + '{1}{0}'.format(rec_str, col_sep)
        rec_line_str = rec_line_str + col_sep
        print(rec_line_str)
    print(header_footer)
    
    
    if print_summary:
        print(col_sep + sumarry.ljust(len(row_delimiter)-2) + col_sep)
        print(header_footer)


if __name__ == '__main__':
    help(print_table)

