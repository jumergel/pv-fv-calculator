#FORMULAS
def pv_annuity(cf, rate, periods):
    if rate == 0:
        return cf * periods
    cr_rate = cf / rate
    return cr_rate * (1 - (1 / ((1 + rate) ** periods)))

def fv_annuity(cf, rate, periods):
    if rate == 0:
        return cf * periods
    return cf * ((((1 + rate) ** periods) - 1) / rate)

def fv_growing_annuity(cf1, rate, growth, periods):
    if rate == growth:
        return cf1 * periods * (1 + rate) ** (periods - 1)
    cr_rate1 = cf1 / (rate - growth)
    return cr_rate1 * ((1 + rate) ** periods - (1 + growth) ** periods)

def pv_perpetuity(cf, rate):
    return cf / rate

def pv_growing_annuity(cf1, rate, growth, periods):
    if rate == growth:
        return cf1 * periods / (1 + rate)
    cr_rate1 = cf1 / (rate - growth)
    return cr_rate1 * (1 - ((1 + growth) / (1 + rate)) ** periods)

def pv_growing_perpetuity(cf1, rate, growth):
    return cf1 / (rate - growth)


#MAIN CALCULATION
def calculate(value_type, periods, rate, cf, growth_phases, phases):
    total = 0.0
    total_periods = periods
    log = []

    if periods > 0:
        if value_type == "PV":
            discrete_result = pv_annuity(cf, rate, periods)
            total += discrete_result
        else:
            discrete_result = fv_annuity(cf, rate, periods)
            total = discrete_result
        log.append(f"{value_type} Discrete Forecast: ${discrete_result:,.2f}")

    last_cf = cf

    for i in range(growth_phases):
        phase = phases[i]
        growth = phase["growth"]

        if value_type == "PV":
            cf1 = last_cf * (1 + growth)
            growth_type = phase.get("type", "annuity")

            if growth_type == "annuity":
                phase_length = phase["length"]
                phase_value = pv_growing_annuity(cf1, rate, growth, phase_length)
                result = phase_value / ((1 + rate) ** total_periods)
                last_cf = cf1 * (1 + growth) ** (phase_length - 1)
                total_periods += phase_length
                log.append(f"PV Phase {i + 1} Annuity: ${result:,.2f}")
            elif growth_type == "perpetuity":
                if growth >= rate:
                    raise ValueError("Perpetuity growth rate must be less than the discount rate.")
                phase_value = pv_growing_perpetuity(cf1, rate, growth)
                result = phase_value / ((1 + rate) ** total_periods)
                log.append(f"PV Phase {i + 1} Perpetuity: ${result:,.2f}")
            else:
                raise ValueError("Please enter either annuity or perpetuity.")

            total += result

        else:
            cf1 = last_cf * (1 + growth)
            phase_length = phase["length"]
            result = fv_growing_annuity(cf1, rate, growth, phase_length)
            last_cf = cf1 * (1 + growth) ** (phase_length - 1)
            log.append(f"FV Phase {i + 1} Annuity: ${result:,.2f}")
            total = total * (1 + rate) ** phase_length + result

    log.append(f"Total {value_type} = ${total:,.2f}")
    return total, log
