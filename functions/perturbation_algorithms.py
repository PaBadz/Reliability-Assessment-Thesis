# import numpy as np
# import streamlit as st
# import json
#
#
# # Cardinal perturbation
# def percentage_perturbation(percentage_steps, value):
#     # perturbation within a certain percentage range
#     # feature has to be cardinal in order to be accessed
#     # feature is increased and decreased in percentage steps
#     # perturbation level is orange
#     perturbedList = list()
#     perturbedList.append(value)
#     for i in range(-percentage_steps, percentage_steps+1):
#         if i == 0:
#             pass
#         else:
#             new_value = value * i / 100 + value
#             perturbedList.append(float(new_value))
#             # print(new_value)
#     return perturbedList
#
# def percentage_perturbation_settings(percentage_steps, value):
#     settings = dict()
#     settings['percentage_steps'] = percentage_steps
#     settings['value'] = value
#     return settings
#
# def sensorPrecision(sensorPrecision: float, steps: int, value):
#     perturbedList = list()
#     for i in range(-steps, steps + 1):
#         if i == 0:
#             pass
#         else:
#             perturbed_value = value * (1 + (sensorPrecision / 1000) * i)
#             perturbedList.append(float(perturbed_value))
#             # print('{0:.100f}'.format(perturbed_value))
#     return perturbedList
#
# def sensorPrecision_settings(sensorPrecision, steps, value):
#     settings = dict()
#     settings['sensorPrecision'] = sensorPrecision
#     settings['steps'] = steps
#     settings['value'] = value
#     return settings
#
# def fixedAmountSteps(amount, steps, value):
#     perturbedList = list()
#     for i in range(-steps, steps + 1):
#         if i == 0:
#             pass
#         else:
#             perturbed_value = value + amount * i
#             perturbedList.append(float(perturbed_value))
#             # print(perturbed_value)
#     return perturbedList
#
# def fixedAmountSteps_settings(amount, steps, value):
#     settings = dict()
#     settings['amount'] = amount
#     settings['steps'] = steps
#     settings['value'] = value
#     return settings
#
# def perturbRange(lowerBound, upperBound, steps):
#     perturbedList = list()
#     range_ = upperBound - lowerBound
#
#     for i in range(0, steps + 1):
#         perturbed_value = lowerBound + (range_ / steps * i)
#         perturbedList.append(perturbed_value)
#         # print(perturbed_value)
#     return perturbedList
#
# def perturbRange_settings(lowerBound, upperBound, steps):
#     settings = dict()
#     settings['lowerBound'] = lowerBound
#     settings['upperBound'] = upperBound
#     settings['steps'] = steps
#     return settings
#
#
# # ordinal perturbation
# def perturbInOrder(steps, value, values):
#     perturbedList = list()
#     size = len(values)
#
#     ind = values.index(value)
#     # perturbedList.append((value))
#     for i in range(1, steps + 1):
#         if ind - i >= 0:
#             perturbedList.append(values[ind - i])
#             # print(values[ind - i])
#     for i in range(1, steps + 1):
#         if ind + i < size:
#             perturbedList.append(values[ind + i])
#             # print(values[ind + i])
#
#     st.write(perturbedList)
#     return perturbedList
#
# def perturbInOrder_settings(steps, value, values):
#     settings = dict()
#     settings['steps'] = steps
#     settings['value'] = value
#     settings['values'] = values
#     return settings
#
# # nominal & ordinal perturbation
# def perturbAllValues(value, values):
#     perturbedList = list()
#     size = len(values)
#
#     ind = values.index(value)
#     perturbedList.append((value))
#     for i in range(1, size + 1):
#         if ind - i >= 0:
#             perturbedList.append(values[ind - i])
#
#     for i in range(1, size + 1):
#         if ind + i < size:
#             perturbedList.append(values[ind + i])
#
#     return perturbedList
#
# def perturbAllValues_settings(value, values):
#     settings = dict()
#     settings['value'] = value
#     settings['values'] = values
#     return settings
#
# # from sklearn import datasets
# # import pandas as pd
# # with open("/Users/pascal/Downloads/bank_cleaned.csv") as f:
# #     data = pd.read_csv(f)
# # #
# # # #data = datasets.load_iris()
# # # # df = pd.DataFrame(data=data.data, columns=data.feature_names)
# # df = pd.DataFrame(data=data, columns=data.columns)
# # # print(df.columns)
# # #
# # #
# # job = df['job'].unique()
# # # # job = df['sepal length (cm)'].unique()
# # # #job=job.tolist()
# # print(type(job))
# # # a = ["a","b","c"]
# # # # b = ["a","b","c"]
# # li = perturbAllValues("technician",job)
# # # #
# # # print(li)
# # ind=np.where(job == "technician")[0][0]
# # print(ind)
# # print(job)