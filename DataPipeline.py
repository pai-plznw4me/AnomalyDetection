import pandas as pd
import os
import collections
from glob import glob


def parsing(fpath):
    """
    파일 하나를 parsing 함.
    :return:
    """

    f = open(fpath, encoding='UTF-8')

    # read sample
    # Eval function 을 사용하기 위해서 해당 txt 파일에 있지만 eval 할 수 없는 변수들을 지정함
    null = None
    false = False
    true = True

    # txt file parsing
    data = []
    buy_hists = []
    len_7 = []
    len_5 = []

    len_elements = []
    for line in f.readlines()[:]:
        """
        Log format 은 아래와 같은 종류로 되어 있음
        1. hh:mm:ss \t [ip] \t [type] \t - or WARN \t {json obj} \n
        2. hh:mm:ss \t [ip] \t ip \t [type] \t - or WARN \t {json obj} \n
        
        WARN 이면 b2cBuyHistVOList 가 없다.   
        """

        len_elements.append(len(line.split('\t')))

        try:

            if len(line.split('\t')[:]) == 5:
                time, log_id, cls, state, obj = line.split('\t')[:]
                len_5.append(line.split('\t')[:])

            elif len(line.split('\t')[:]) == 7:
                time, log_id, ip, cls, state, _,  obj = line.split('\t')[:]
                len_7.append(line.split('\t')[:])

            elif len(line.split('\t')[:]) == 1:
                continue

            else:
                n_type = set((len_elements))
                print(n_type, line)

            obj = eval(obj)
            obj['type'] = cls

            if state == '-':
                # 해당 obj 는 Nested Dict 구조로 되어 있음
                # Nested 된 column name 은 b2cBuyHistVOList 임.
                # b2cBuyHistVOList 은 [obj] 구조로 되어 있음
                # * Warning, db 구조에 문제가 있는듯 왜 list 로 쌓여 있는거지? => 모든 경우의 수를 check 해야 함.*
                obj['b2cBuyHistVOList'] = obj['b2cBuyHistVOList'][0]

                # 데이터를 list에 쌓음
                buy_hists.append(obj['b2cBuyHistVOList'])
                data.append(obj)

        except IndexError as ie:
            # Error Case
            # Log 가 기록된 날짜를 지정한 Row
            print(line)
        except ValueError as ve:
            print(line)

        except KeyError as ke:
            pass;

    list(map(print, len_5[:10]))
    list(map(print, len_7[:10]))

    # Dict 2 DataFrame
    df = pd.DataFrame.from_dict(data)
    sub_df = pd.DataFrame.from_dict(buy_hists)

    # Feature analysis
    # 겹치는 Feature
    # earnMileage': 2, 'payId': 2, 'sc': 2, 'userNo': 2,
    # earnMileage 는 None 값이 들어가 있는데 DB에서 잘 못 feature 가 들어간듯

    columns_names = df.columns.values.tolist() + sub_df.columns.values.tolist()
    n_log = len(df)
    print('총 Feature : {}'.format(len(set(columns_names))))
    print('total # Log : {}'.format(n_log))
    print(len(set(len_elements)))
    print(set(len_elements))


if __name__ == '__main__':
    # open sample
    sample_path = os.path.join('./', 'sample', 'payment-201907.txt')
    f = open(sample_path, encoding='UTF-8')
    parsing(sample_path)