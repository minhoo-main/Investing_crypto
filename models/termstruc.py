import numpy as np

class InterestTermStructure:
    def __init__(self, currency, df_price_data, df_instrument_data):
        self.currency = currency
        self.df_price_data = df_price_data
        self.df_instrument_data = df_instrument_data
        self.seconds_in_a_year = 365 * 24 * 60 * 60
        self.milliseconds_in_a_year = self.seconds_in_a_year * 1000
        
    def mapping_info(self, series_symbol, item):
        ls_symbol = series_symbol.index
        return [self.df_instrument_data[symbol][item] for symbol in ls_symbol] 

    def price_to_zrate(self, dt_tdate, series_data): #(1)
        ts_tdate = dt_tdate.timestamp() * 1000
        
        ls_x_ts_time = self.mapping_info(series_data, 'expiration_timestamp')
        ls_settle_type = self.mapping_info(series_data, 'settlement_period')
        ls_y_price = list(series_data.values)
        
        perp_index = ls_settle_type.index('perpetual')
        perp_price = ls_y_price.pop(perp_index)
        ls_x_ts_time.pop(perp_index)
        ls_time = [(ts - ts_tdate) / self.milliseconds_in_a_year for ts in ls_x_ts_time]
        
        ls_y_zrate = [np.log(y / perp_price) / x for x,y in zip(ls_time, ls_y_price)]
        return ls_time, ls_y_zrate
   
    def get_zrate(self, dt_tdate, dt_T): #(0) (3)
       '''
       Parameters
       ----------
       ts_tdate : datetime.datetime
           valueation date. (time at t0 = 0)
       ts_T : datetime.datetime
           maturity date. (time at T)
           
       Returns
       -------
       zrate : float
           zero rate at time T
       '''
       
       series_data = self.df_price_data.loc[dt_tdate].dropna()
       
       ls_x_time, ls_y_zrate = self.price_to_zrate(dt_tdate, series_data)
       t = (dt_T.timestamp() * 1000 - dt_tdate.timestamp() * 1000) / self.milliseconds_in_a_year
       
       return self.ccfr_interpolation(ls_x_time, ls_y_zrate, t)
       
    def ccfr_interpolation(self, ls_x_time, ls_y_zrate, x_t): #(2)
        '''
        constant continuous forward rates interpolation method 
        -> easy and most commonly used method
        Define zero rate:= exp(-r*t -f*(T-t)) where f = (r(T)*T - r(t)*t)/(T-t)
        '''
        if len(ls_x_time) != len(ls_y_zrate):
            return None
        
        i_x0, i_x1 = self.find_closest_indices(ls_x_time, x_t)
        if i_x0 == None:
            return ls_y_zrate[i_x1]
        elif i_x1 == None:
            return ls_y_zrate[i_x0]
        else:
            x0, x1 = ls_x_time[i_x0], ls_x_time[i_x1]
            y0, y1 = ls_y_zrate[i_x0], ls_y_zrate[i_x1]
            f = (y1 * x1 - y0 * x0) / (x1 - x0)
            dcf = np.exp(-y0 * x0 -f * (x1 - x0))
            return -np.log(dcf) / x1
            
    def find_closest_indices(self, ls, x0):
        smaller_than_threshold_indices = [i for i, x in enumerate(ls) if x < x0]
        larger_than_threshold_indices = [i for i, x in enumerate(ls) if x > x0]
    
        if smaller_than_threshold_indices:
            max_smaller_index = max(smaller_than_threshold_indices)
        else:
            max_smaller_index = None
    
        if larger_than_threshold_indices:
            min_larger_index = min(larger_than_threshold_indices)
        else:
            min_larger_index = None  

        return max_smaller_index, min_larger_index