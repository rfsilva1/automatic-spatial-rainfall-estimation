#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import numpy as np
import math
from datetime import datetime
import sys
# Make sure to import from the original functions file
from funcoes_orig import *

def run_original_script(threshold, alpha):
    # Corrected file paths
    coord_gauges = 'dataset/estacoes_planicie.xlsx'
    # This is a guess based on the file list and original path
    data = 'dataset/dados_chuva_planicie.xlsx'

    # Load data
    df_coord = pd.read_excel(coord_gauges)
    df_coord['Gauge'] = df_coord['Gauge'].astype(str)
    coords = df_coord.set_index('Gauge').T.to_dict()

    gauge_data = pd.read_excel(data)
    gauge_data = gauge_data.set_index(['Date'])
    gauge_data.columns = [str(c) for c in gauge_data.columns]

    # This is the original logic to get the list of gauges per day
    filter_gauges = gauge_data.notna().dot(gauge_data.columns+',').str.rstrip(',')
    mylist = filter_gauges.values.tolist()
    gauge_list = []
    for l in mylist:
        gauge_list.append(l.split(','))

    # Main processing loop from the original script
    lista2 = []
    for i, list_gauges in enumerate(gauge_list):
        rainfall_values = gauge_data.iloc[i].dropna().tolist()
        if len(rainfall_values) < 2:
            continue

        # Call the original idw_all function
        final_idw = idw_all(list_gauges, rainfall_values, threshold, coords, alpha)
        if final_idw[0]: # Check if idw_all returned any values
            lista2.append(final_idw)

    if not lista2:
        print("Original script produced no results.")
        return

    # Post-processing from the original script
    lista2 = pd.DataFrame(lista2, columns=['idw_values', 'gauges', 'unknow_id', 'real_values'])

    # It seems the original code could produce empty lists, let's filter them
    lista2 = lista2[lista2['idw_values'].map(len) > 0].copy()

    lista2['n_gauges'] = lista2['gauges'].apply(count_gauges)

    def sMAPEabs(sim, obs):
        return [abs(o-s) for s, o in zip(sim, obs)]

    def sMAPErel(sim, obs):
        return [o+s for s, o in zip(sim, obs)]

    lista2['erro_abs'] = lista2.apply(lambda x: sMAPEabs(x['idw_values'], x['real_values']), axis=1)
    lista2['erro_rel'] = lista2.apply(lambda x: sMAPErel(x['idw_values'], x['real_values']), axis=1)

    def convert2tuple(x):
        return list(zip(x['n_gauges'], x['erro_abs'], x['erro_rel']))

    lista2['tuples'] = lista2.apply(convert2tuple, axis=1)

    df = lista2[['tuples']].explode('tuples').reset_index(drop=True)

    df[['qtde', 'erro_abs', 'erro_rel']] = pd.DataFrame(df['tuples'].tolist(), index=df.index)
    df = df.drop(columns=['tuples'])

    sMAPE = df.groupby('qtde').sum().reset_index()
    # Handle division by zero
    sMAPE['erro'] = sMAPE['erro_abs'].divide(sMAPE['erro_rel']).fillna(0)

    # Define output filename
    output_filename = f"sMAPE_orig_{alpha}_{threshold}.xlsx"
    sMAPE.to_excel(output_filename, index=False)
    print(f"Original script finished. Results saved to {output_filename}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python method_IDW_orig.py <threshold> <alpha>')
        sys.exit(1)

    threshold_arg = int(sys.argv[1])
    alpha_arg = int(sys.argv[2])

    run_original_script(threshold_arg, alpha_arg)
