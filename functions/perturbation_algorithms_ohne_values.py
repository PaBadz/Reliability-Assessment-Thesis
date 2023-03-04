# Cardinal perturbation
import streamlit as st
def percentage_perturbation(percentage_steps, value, data_restriction):
    # perturbation within a certain percentage range
    # feature has to be cardinal in order to be accessed
    # feature is increased and decreased in percentage steps
    # perturbation level is orange
    perturbedList = list()
    for i in range(-percentage_steps, percentage_steps+1):
        if i == 0:
            pass
        else:
            new_value = round(value * i / 100 + value,2)
            if float(data_restriction[0]) <= float(new_value) <= float(data_restriction[1]):
                perturbedList.append(float(new_value))
            else:
                pass
    return perturbedList

def percentage_perturbation_settings(percentage_steps):
    settings = dict()
    settings['steps'] = percentage_steps
    return settings

def sensorPrecision(sensorPrecision: float, steps: int, value, data_restriction):
    perturbedList = list()
    for i in range(-steps, steps + 1):
        if i == 0:
            pass
        else:
            perturbed_value = round(value * (1 + (sensorPrecision / 100) * i),2)
            if float(data_restriction[0]) <= float(perturbed_value) <= float(data_restriction[1]):
                perturbedList.append(float(perturbed_value))

    return perturbedList

def sensorPrecision_settings(sensorPrecision, steps):
    settings = dict()
    settings['sensorPrecision'] = sensorPrecision
    settings['steps'] = steps
    return settings

def fixedAmountSteps(amount, steps, value, data_restriction):
    perturbedList = list()

    for i in range(-steps, steps + 1):
        if i == 0:
            pass
        else:
            perturbed_value = round(value + amount * i,2)
            if float(data_restriction[0]) <= float(perturbed_value) <= float(data_restriction[1]):
                perturbedList.append(float(perturbed_value))
    return perturbedList

def fixedAmountSteps_settings(amount, steps):
    settings = dict()
    settings['amount'] = amount
    settings['steps'] = steps
    return settings

def perturbRange(lowerBound, upperBound, steps):
    perturbedList = list()
    range_ = upperBound - lowerBound

    for i in range(0, steps + 1):
        perturbed_value = round(lowerBound + (range_ / steps * i),2)
        perturbedList.append(perturbed_value)
    return perturbedList

def perturbRange_settings(lowerBound, upperBound, steps):
    settings = dict()
    settings['lowerBound'] = lowerBound
    settings['upperBound'] = upperBound
    settings['steps'] = steps

    return settings

def perturbBin_settings(steps):
    settings = dict()
    settings['steps'] = steps
    return settings


# ordinal perturbation
def perturbInOrder(steps, value, values):
    perturbedList = list()
    size = len(values)

    ind = values.index(value)
    for i in range(1, steps + 1):
        if ind - i >= 0:
            perturbedList.append(values[ind - i])

    for i in range(1, steps + 1):
        if ind + i < size:
            perturbedList.append(values[ind + i])



    return perturbedList

def perturbInOrder_settings(steps):
    settings = dict()
    settings['steps'] = steps

    return settings



# nominal & ordinal perturbation
def perturbAllValues(value, values):
    perturbedList = list()
    perturbedList.append(value)
    size = len(values)

    ind = values.index(value)
    for i in range(1, size + 1):
        if ind - i >= 0:
            perturbedList.append(values[ind - i])

    for i in range(1, size + 1):
        if ind + i < size:
            perturbedList.append(values[ind + i])

    return perturbedList

def perturbAllValues_settings():
    settings = dict()

    return settings
