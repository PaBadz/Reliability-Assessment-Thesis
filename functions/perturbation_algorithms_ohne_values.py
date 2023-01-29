# Cardinal perturbation
import streamlit as st
def percentage_perturbation(percentage_steps, value, data_restriction):
    # perturbation within a certain percentage range
    # feature has to be cardinal in order to be accessed
    # feature is increased and decreased in percentage steps
    # perturbation level is orange
    perturbedList = list()
    # perturbedList.append(value)
    for i in range(-percentage_steps, percentage_steps+1):
        if i == 0:
            pass
        else:
            new_value = value * i / 100 + value
            if float(data_restriction[0]) <= float(new_value) <= float(data_restriction[1]):
                perturbedList.append(float(new_value))
            else:
                pass
            # print(new_value)
    return perturbedList

def percentage_perturbation_settings(percentage_steps, perturbation_level):
    settings = dict()
    settings['steps'] = percentage_steps
    settings['PerturbationLevel'] = perturbation_level
    return settings

def sensorPrecision(sensorPrecision: float, steps: int, value, data_restriction):
    perturbedList = list()
    # perturbedList.append(value)
    for i in range(-steps, steps + 1):
        if i == 0:
            pass
        else:
            perturbed_value = value * (1 + (sensorPrecision / 1000) * i)
            if float(data_restriction[0]) <= float(perturbed_value) <= float(data_restriction[1]):
                perturbedList.append(float(perturbed_value))

    return perturbedList

def sensorPrecision_settings(sensorPrecision, steps, perturbation_level):
    settings = dict()
    settings['sensorPrecision'] = sensorPrecision
    settings['steps'] = steps
    settings['PerturbationLevel'] = perturbation_level
    return settings

def fixedAmountSteps(amount, steps, value, data_restriction):
    perturbedList = list()
    # perturbedList.append(value)
    for i in range(-steps, steps + 1):
        if i == 0:
            pass
        else:
            perturbed_value = value + amount * i
            if float(data_restriction[0]) <= float(perturbed_value) <= float(data_restriction[1]):
                perturbedList.append(float(perturbed_value))
            # print(perturbed_value)
    return perturbedList

def fixedAmountSteps_settings(amount, steps, perturbation_level):
    settings = dict()
    settings['amount'] = amount
    settings['steps'] = steps
    settings['PerturbationLevel'] = perturbation_level
    return settings

def perturbRange(lowerBound, upperBound, steps):
    perturbedList = list()
    range_ = upperBound - lowerBound

    for i in range(0, steps + 1):
        perturbed_value = lowerBound + (range_ / steps * i)
        perturbedList.append(perturbed_value)
        # print(perturbed_value)
    return perturbedList

def perturbRange_settings(lowerBound, upperBound, steps, perturbation_level):
    settings = dict()
    settings['lowerBound'] = lowerBound
    settings['upperBound'] = upperBound
    settings['steps'] = steps
    settings['PerturbationLevel'] = perturbation_level
    return settings

def perturbBin_settings(steps,perturbation_level):
    settings = dict()
    settings['steps'] = steps
    settings['PerturbationLevel'] = perturbation_level
    return settings


# ordinal perturbation
def perturbInOrder(steps, value, values):
    perturbedList = list()
    size = len(values)

    ind = values.index(value)
    # perturbedList.append(value)
    for i in range(1, steps + 1):
        if ind - i >= 0:
            perturbedList.append(values[ind - i])
            # print(values[ind - i])
    for i in range(1, steps + 1):
        if ind + i < size:
            perturbedList.append(values[ind + i])
            # print(values[ind + i])


    return perturbedList

def perturbInOrder_settings(steps,perturbation_level):
    settings = dict()
    settings['steps'] = steps
    settings['PerturbationLevel'] = perturbation_level
    #settings['values'] = values
    return settings



# nominal & ordinal perturbation
def perturbAllValues(value, values):
    perturbedList = list()
    perturbedList.append(value)
    size = len(values)

    ind = values.index(value)
    #perturbedList.append((value))
    for i in range(1, size + 1):
        if ind - i >= 0:
            perturbedList.append(values[ind - i])

    for i in range(1, size + 1):
        if ind + i < size:
            perturbedList.append(values[ind + i])

    return perturbedList

def perturbAllValues_settings(perturbation_level):#value
    settings = dict()
    # settings['value'] = value
    settings['PerturbationLevel'] = perturbation_level
    # settings['values'] = values
    return settings
