import numpy as np

def no_exception(f, v):
    success = True
    try:
        f(v)
    except Exception as e:
        print(e)
        success = False
    return success

def find_range(f, guess, fail_range, converge_diff, step_up_size, step_down_size = None, min = None, max = None):
    if step_down_size == None:
        step_down_size = step_up_size
    
    # Remove units
    units = guess.unit
    fail_range = fail_range.to(units).value
    step_up_size = step_up_size.to(units).value
    step_down_size = step_down_size.to(units).value
    converge_diff = converge_diff.to(units).value
    if min != None:
        min = min.to(units).value
    if max != None:
        max = max.to(units).value
    guess = guess.value

    # First find starting value that works
    start = None
    for dx in (0, fail_range, -fail_range):
        x = guess + dx
        if start == None and no_exception(f, x * units):
            start = x

    if start:
        MAX = None
        MIN = None

        # Find upper bound
        upper = None
        lower = start
        value = start + step_up_size
        while True:
            if no_exception(f, value * units):
                lower = value
                if upper != None:
                    if np.abs(upper - lower) < converge_diff:
                        MAX = lower
                        break
                    else:
                        value = (upper + lower) / 2
                else:
                    value += step_up_size
                if max != None and lower > max:
                    MAX = max
                    break
            else:
                upper = value
                if np.abs(upper - lower) < converge_diff:
                    MAX = lower
                    break
                else:
                    value = (upper + lower) / 2

        # Find lower bound
        upper = start
        lower = None
        value = start - step_down_size
        while True:
            if no_exception(f, value * units):
                upper = value
                if lower != None:
                    if np.abs(upper - lower) < converge_diff:
                        MIN = upper
                        break
                    else:
                        value = (upper + lower) / 2
                else:
                    value -= step_down_size
                if min != None and upper < min:
                    MIN = min
                    break
            else:
                lower = value
                if np.abs(upper - lower) < converge_diff:
                    MIN = upper
                    break
                else:
                    value = (upper + lower) / 2
                
        return {
            "max": MAX * units,
            "min": MIN * units
        }
    else:
        return None
    
def step_through(f, start, step_size, min, max):
    data = {}

    v = start
    while max == None or v < max:
        result = f(v)
        if result != None:
            data[v] = result
            v += step_size
        else:
            break

    v = start - step_size
    while min == None or v > min:
        result = f(v)
        if result != None:
            data[v] = result
            v -= step_size
        else:
            break
    
    if data:
        return data
    else:
        return None