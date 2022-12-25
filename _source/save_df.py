from pandas import DataFrame

def save_csv(path, matrix, name, ind_col=None):
    '''
        Función que permite crear y guardar un dataframe
        input: 
            matrix: la matrix que se va a convertir en dataframe
            name: nombre para guardar el datafreme
            ind_col: índice y columna del dataframe
        return: 
            None
    '''
    if (ind_col):
        df = DataFrame(matrix, index=ind_col, columns=ind_col)
    else:
        df = DataFrame(matrix)    
    df.to_csv(path+'/'+name+'.csv', encoding='latin-1')