#!/usr/bin/env python

import os
import sys
import re
import pandas as pd
import plotly
import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go
from nltk.tokenize import word_tokenize


# set online credentials for plotly
plotly.tools.set_credentials_file(username='ddewitz',
                                  api_key='0UJR1yePEy3DEI3Z3grC')


def main(preprocess=False, plot=False):
    '''highest level function that drives the program

    if preprocess=True:
        tokenize, count, and group df

        return: clean df

    if plot=True:
        create plotly area plot

        return: online and local area plot
    '''

    # PREPROCESS DATA FOR AREA PLOT
    # this takes a bit to run
    if preprocess:
        # Read in Raw File
        # ----------------
        raw_file = '/data/the_office_lines.csv'
        data_path = get_path() + raw_file

        lines = pd.read_csv(data_path, index_col=None)
        print(lines.columns)
        print(lines.shape)

        # Convert season to string data type
        # ----------------------------------
        lines['season'] = lines['season'].astype(str)
        print(lines)

        # Word Tokenize
        # --------
        lines_word_tok = word_tok_loop(lines)
        print(lines_word_tok['word_tok'])

        # Count Words
        # -----------
        lines_counted = count_words_loop(lines_word_tok)
        print(lines_counted.columns)
        # exit()

        # Group: speaker, season, count
        # -----------------------------
        grouped = lines_counted[['speaker', 'season', 'word_count']].groupby(['speaker', 'season']).sum()
        print(grouped)

        # group: speaker, season
        grouped_slim = lines_counted[['speaker', 'season', 'word_count']].groupby(['speaker']).sum()
        print(grouped_slim)

        out_file_1 = '/output/word_tok.csv'
        out_file_2 = '/output/word_tok_speaker.csv'
        out_path_1 = get_path() + out_file_1
        out_path_2 = get_path() + out_file_2

        grouped.to_csv(out_path_1)
        grouped_slim.to_csv(out_path_2)

    # CREATE AREA PLOT
    if plot:
        area_plot()


def area_plot():
    '''Build Plotly Area Plot graphing the word count
       for each main character over every season of
       The Office

       Data:
          func reads in final data set from preprocessing
          - tokenizing takes some time, so reading data in
            from a csv was more efficient for this project

       Return:
          online and local Plotly Area Plot
    '''
    raw_file = '/output/word_tok.csv'
    data_path = get_path() + raw_file

    grouped = pd.read_csv(data_path, index_col=None)

    print(grouped.columns)
    print(grouped.shape)

    # characters ranked by overall word count
    characters = ['Michael',
                  'Dwight',
                  'Jim',
                  'Pam',
                  'Andy',
                  'Angela',
                  'Kevin',
                  'Ryan',
                  'Erin',
                  'Oscar',
                  'Darryl',
                  'Kelly',
                  'Jan',
                  'Toby',
                  'Phyllis',
                  'Nellie',
                  'Stanley',
                  'Gabe',
                  'Robert',
                  'Holly',
                  'Meredith',
                  'Creed',
                  'David Wallace',
                  'Todd Packer']

    traces = []
    for actor in characters:
        print(actor)

        # I only want to plot the top characters on page load
        if (
            actor != 'Michael' and actor != 'Dwight' and
            actor != 'Jim' and actor != 'Pam' and actor != 'Andy'
           ):
            viz = 'legendonly'
        else:
            viz = True

        actor = go.Scatter(
            x=grouped['season'][grouped['speaker'] == actor],
            y=grouped['word_count'][grouped['speaker'] == actor],
            fill='tozeroy',
            name=actor,
            visible=viz
        )
        traces.append(actor)

    layout = go.Layout(
        autosize=True,
        xaxis=dict(
            title='Season',
            fixedrange=True,
            titlefont=dict(
                family='Arial',
                size=18,
                color='#7f7f7f'
            ),
            tickfont=dict(
                family='Arial',
                size=18,
                color='black'
            )
        ),
        yaxis=dict(
            title='Word Count',
            fixedrange=True,
            titlefont=dict(
                family='Arial',
                size=18,
                color='#7f7f7f'
            ),
            tickfont=dict(
                family='Arial',
                size=16,
                color='black'
            )
        ),
        legend=dict(
            font=dict(
                family='Arial',
                size=16,
                color='black'
            )
        )
    )

    # show plot online and local
    fig = dict(data=traces, layout=layout)
    offline.plot(fig, filename='the_office_area_plot_web.html')
    py.plot(fig, filename='the_office_area_plot_web.html')

    print(traces)
    exit()


def count_words_loop(df):
    # for loop to apply word count func
    df['word_count'] = df.apply(count_words, axis=1)
    return df


def count_words(row):
    # count each tokenized row
    count = len(row.word_tok)
    print(row.speaker)
    print(count)
    return count


def word_tok_loop(df):
    # for loop to tokenize each row
    df['word_tok'] = df.apply(word_tok, axis=1)
    return df


def word_tok(row):
    '''text preprocessing function

    1. remove stage instructions in brackets
    2. trim white space
    3. tokenize
    4. remove special characters

    arg:
        row of a df

    return:
        clean, tokenized row
    '''

    # remove stage instructions in brackets
    no_brackets = re.sub("[\(\[].*?[\)\]]", "", row.line_text)

    # trim white space
    no_white = no_brackets.strip()

    # tokenize words
    word_tokens = word_tokenize(no_white)

    # lowercase all words
    lower_tokens = [tok.lower() for tok in word_tokens]

    # remove special characters
    alpha_only = [tok for tok in lower_tokens if tok.isalpha()]

    print(row.speaker)
    print(alpha_only)

    return alpha_only


def get_path():
    # simple dynamic file path
    pathname = os.path.dirname(sys.argv[0])
    abs_path = os.path.abspath(pathname)
    return abs_path


if __name__ == "__main__":
    main(plot=True)
