//@version=6
// ══════════════════════════════════════════════════════════════════════════════════════════════════ //
//# * ══════════════════════════════════════════════════════════════════════════════════════════════
//# *
//# * Study       : HTF Candles & Mini Charts
//# * Author      : © dgtrd
//# *
//# * Revision History
//# *  Release    : May 29, 2021
//# *  Update     : May 29, 2021 : Added performance statistics
//# *  Update     : Jun 12, 2021 : Added moving averages and extended performance statistics
//# *  Update     : Jun 14, 2021 : Added Heikin Ashi support
//# *  Update     : Jun 29, 2021 : Added second HTF candle plotting
//# *  Update     : Jul 01, 2021 : Introduced Mini HTF Charts
//# *  Update     : Jul 15, 2021 : Enhanced Mini HTF Charts
//# *  Update     : Jan 31, 2022 : Added 5-period SMA overlay for Mini HTF Charts
//# *  Update     : Jun 14, 2022 : Added new indicators
//# *                               - Volume Weighted Colored Bars
//# *                               - Mini Overlay RSI indicator (including higher-timeframe mini charts)
//# *                               - Forex Market Sessions
//# *  Update     : Jul 27, 2022 : Added support for multiple moving averages on HTF mini charts
//# *  Update     : Oct 17, 2022 : Refactored Mini Charts engine
//# *                               - Improved and extended HTF mini charts
//# *                               - Added candlestick pattern detection
//# *                               - Enhanced statistical panel
//# *                               - Extended alert capabilities
//# *                               - Removed Forex Market Sessions display
//# * Update     : Mar 2026 : Complete architectural redesign
//# *                              - Rebuilt HTF engine
//# *                              - New mini chart rendering framework
//# *                              - Expanded technical overlay framework (Supertrend, Bollinger Bands, Moving Averages)
//# *                              - Extended oscillator integration (RSI / Stochastic)
//# *                              - Improved volume-weighted candle logic
//# *                              - Refined statistical panel
//# *                              - Optimized performance and lookback handling
//# *                              - Removed candlestick pattern detection
//# *
//# * ══════════════════════════════════════════════════════════════════════════════════════════════
// ══════════════════════════════════════════════════════════════════════════════════════════════════ //

indicator('HTF Candles by DGT', 'HTF+ ☼☾', true, max_lines_count = 500, max_boxes_count = 500)//, max_bars_back = 5000)

//---------------------------------------------------------------------------------------------------------------------//
// Settings 


display = display.all - display.status_line

htf1GR = 'First HTF Chart'

htf1SH = input.bool(true, 'First HTF on Main Chart', group = htf1GR,
     tooltip = 'Displays the first higher-timeframe (HTF) chart overlaid on the main price chart.')
htf1TF = input.string('Chart', '  Timeframe', group = htf1GR, display = display,
     options = ['Chart', '1 Minute', '3 Minutes', '5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '2 Hours', '4 Hours', '12 Hours', '1 Day', '1 Week', '1 Month'], 
     tooltip = 'Select the timeframe used to construct the higher-timeframe chart.\n\n' +
                 '"Chart" uses the current chart timeframe.\n\n' +
                 'If the selected timeframe is lower than the chart timeframe, the effective timeframe automatically defaults to the chart timeframe.')
htf1CT = input.string('Candles', '  Chart Type', group = htf1GR, display = display,
     options = ['Candles', 'High-Low', 'Heikin Ashi'], 
     tooltip ='Select how the HTF candles are rendered.\n\n' +
                 'Heikin Ashi uses synthetic candles derived from price data.')
htf1VWs   = input.string('Off', '  Volume-Weighted Candles', options = ['On', 'Off'], group=htf1GR, display = display,
     tooltip = 'Colors higher-timeframe candles based on volume relative to its moving average.'), htf1VW = htf1VWs == 'On'
htf1BLClr = input.color(color.teal, '  ', inline = 'tf1', group = htf1GR)
htf1BRClr = input.color(color.red, '', inline = 'tf1', group = htf1GR)
htf1ClrT  = input.int(85, 'Transparency', minval = 0, maxval = 100, inline = 'tf1', group = htf1GR, display = display)

htf1SHm = input.bool(true, 'Mini HTF Chart', group = htf1GR,
     tooltip ='Displays a miniature higher-timeframe chart to the right of the current chart.')
htf1NB = input.int(41, '  Mini Chart Bars', minval = 1, maxval = 73, group = htf1GR, display = display, 
     tooltip = 'Number of higher-timeframe bars displayed in the mini chart.\n\n' +
                 'Maximum supported value is 73.')
htf1TI = input.string('Supertrend', '  Mini Chart Overlay', group = htf1GR, display = display,
     options = ['None', 'Bollinger Bands', 'Moving Average', 'Supertrend'], 
     tooltip = 'Technical indicator displayed on the mini HTF chart.')
htf1OI = input.string('RSI', '  Mini Chart Oscillator', group = htf1GR, display = display,
     options = ['None', 'RSI', 'Stochastic'], 
     tooltip = 'Momentum oscillator displayed beneath the mini HTF chart.')
htf1RL = input.string('Range Quartiles', '  Reference Levels', 
     options=['None', 'Range Extremes', 'Range Quartiles'], group = htf1GR, display = display,
     tooltip = 'Displays statistical reference levels derived from the mini chart range.\n\n' +
                 'Range Extremes → Highest high and lowest low\n' +
                 'Range Quartiles → Adds 25%, 50%, and 75% levels')
htf1VWms   = input.string('Off', '  Volume-Weighted Candles', options = ['On', 'Off'], group=htf1GR, display = display,
     tooltip = 'Applies volume-weighted coloring to candles in the mini HTF chart.'), htf1VWm = htf1VWms == 'On'
htf1LBs = input.string('On', '  Mini Chart Labels', options = ['On', 'Off'], group = htf1GR, display = display,
     tooltip = 'Displays descriptive labels for the mini chart and reference levels.'), htf1LB = htf1LBs == 'On'
htf1SZ = input.int(13, '  Mini Chart Offset', minval = 10, maxval = 100, group = htf1GR, display = display,
     tooltip = 'Horizontal offset used to position the mini chart to the right of the price chart.')

htf2GR = 'Second HTF Chart'

htf2SH = input.bool(false, 'Second HTF on Main Chart', group = htf2GR,
     tooltip = 'Displays the second higher-timeframe (HTF) chart overlaid on the main price chart.')
htf2TF = input.string('Chart', '  Timeframe', group = htf2GR, display = display,
     options = ['Chart', '1 Minute', '3 Minutes', '5 Minutes', '15 Minutes', '30 Minutes', '1 Hour', '2 Hours', '4 Hours', '12 Hours', '1 Day', '1 Week', '1 Month'], 
     tooltip = 'Select the timeframe used to construct the higher-timeframe chart.\n\n' +
                 '"Chart" uses the current chart timeframe.\n\n' +
                 'If the selected timeframe is lower than the chart timeframe, the effective timeframe automatically defaults to the chart timeframe.')
htf2CT = input.string('Candles', '  Chart Type', group = htf2GR, display = display,
     options = ['Candles', 'High-Low', 'Heikin Ashi'], 
     tooltip ='Select how the HTF candles are rendered.\n\n' +
                 'Heikin Ashi uses synthetic candles derived from price data.')
htf2VWs   = input.string('Off', '  Volume-Weighted Candles', options = ['On', 'Off'], group=htf2GR, display = display,
     tooltip = 'Colors higher-timeframe candles based on volume relative to its moving average.'), htf2VW = htf2VWs == 'On'
htf2BLClr = input.color(color.teal, '  ', inline = 'tf2', group = htf2GR)
htf2BRClr = input.color(color.red, '', inline = 'tf2', group = htf2GR)
htf2ClrT  = input.int(90, 'Transparency', minval = 0, maxval = 100, inline = 'tf2', group = htf2GR, display = display)

htf2SHm = input.bool(false, 'Mini HTF Chart', group = htf2GR,
     tooltip ='Displays a miniature higher-timeframe chart to the right of the current chart.')
htf2NB = input.int(21, '  Mini Chart Bars', minval = 1, maxval = 73, group = htf2GR, display = display, 
     tooltip = 'Number of higher-timeframe bars displayed in the mini chart.\n\n' +
                 'Maximum supported value is 73.')
htf2TI = input.string('Moving Average', '  Mini Chart Overlay', group = htf2GR, display = display,
     options = ['None', 'Bollinger Bands', 'Moving Average', 'Supertrend'], 
     tooltip = 'Technical indicator displayed on the mini HTF chart.')
htf2OI = input.string('Stochastic', '  Mini Chart Oscillator', group = htf2GR, display = display,
     options = ['None', 'RSI', 'Stochastic'], 
     tooltip = 'Momentum oscillator displayed beneath the mini HTF chart.')
htf2RL = input.string('Range Extremes', '  Reference Levels', 
     options=['None', 'Range Extremes', 'Range Quartiles'], group = htf2GR, display = display,
     tooltip = 'Displays statistical reference levels derived from the mini chart range.\n\n' +
                 'Range Extremes → Highest high and lowest low\n' +
                 'Range Quartiles → Adds 25%, 50%, and 75% levels')
htf2VWms   = input.string('Off', '  Volume-Weighted Candles', options = ['On', 'Off'], group=htf2GR, display = display,
     tooltip = 'Applies volume-weighted coloring to candles in the mini HTF chart.'), htf2VWm = htf2VWms == 'On'
htf2LBs = input.string('On', '  Mini Chart Labels', options = ['On', 'Off'], group = htf2GR, display = display,
     tooltip = 'Displays descriptive labels for the mini chart and reference levels.'), htf2LB = htf2LBs == 'On'
htf2SZ = input.int(13, '  Mini Chart Offset', minval = 10, maxval = 100, group = htf2GR, display = display,
     tooltip = 'Horizontal offset used to position the mini chart to the right of the price chart.')

chartGR = 'Main Chart Indicators'
chartTI = input.string('None', '  Chart Overlay', group = chartGR, display = display,
     options = ['None', 'Bollinger Bands', 'Moving Average Ribbon', 'Supertrend'], 
     tooltip = 'Select a technical indicator to display directly on the main chart.')
chartOI = input.string('None', '  Chart Oscillator', group = chartGR, display = display,
     options = ['None', 'RSI', 'Stochastic'], 
     tooltip = 'Select a momentum oscillator to display beneath the main chart.')
chartVWs   = input.string('Off', '  Volume-Weighted Candles', options = ['On', 'Off'], group = chartGR, display = display,
     tooltip = 'Colors price bars based on current volume relative to its moving average.\n\n' +
               'Highlights conviction-driven activity and abnormal participation shifts.'), chartVW = chartVWs == 'On'

group_stat = 'Statistic Panel'

chgStat = input.bool(true, 'Performance Metrics', group = group_stat,
     tooltip = 'Displays performance metrics such as returns from the start of the day, week, month, and year.')
pmaStat = input.bool(true, 'Price Distance to MA', group = group_stat,
     tooltip = 'Shows the multi-timeframe distance between price and its moving averages.')
volStat = input.bool(true, 'Volume Statistics', inline = 'VOL', group = group_stat,
     tooltip = 'Displays volume statistics including relative activity and volume behavior across timeframes.')
statSize = input.string('Small', '  Panel Text Size', options = ['Tiny', 'Small', 'Normal'], group = group_stat, display = display)
textSize = statSize == 'Small' ? size.small : statSize == 'Normal' ? size.normal : size.tiny

bbGR = 'Bollinger Bands (Chart + Mini Charts)'
bbType = input.string('SMA', '  Basis Type', options = ['SMA', 'EMA', 'HMA', 'RMA', 'WMA', 'VWMA'], group = bbGR, display = display)
bbSource = input.source(close, '  Source', group = bbGR, display = display)
bbLength = input.int(20, '  Length', minval = 1, group = bbGR, display = display)
bbMult = input.float(2.0, '  Standard Deviation', minval = 0.01, maxval = 50, group = bbGR, display = display)
bbbColor = input.color(color.new(color.orange, 50), '  Color Basis', inline = 'BB', group = bbGR)
bbuColor = input.color(color.blue, 'Bands', inline = 'BB', group = bbGR)

maGR = 'Moving Average (Chart + Mini Charts)'
maType = input.string('SMA', '  Type', 
     options = ['SMA', 'EMA', 'HMA', 'RMA', 'WMA', 'VWMA'], group = maGR, display = display,
     tooltip = 'Select the moving average type used across overlays and mini charts.')
maSource = input.source(close, '  Source', group = maGR, display = display)
maLength = input.int(5, '  Length', minval = 1, group = maGR, display = display,
     tooltip = 'Length used for moving averages displayed in mini charts.')
maColor = input.color(color.blue, '  Color', group = maGR)
ma20Color  = input.color(#00c8ff, '  Ribbon', inline = 'RIB', group = maGR,
     tooltip = 'Colors used for the moving average ribbon displayed on the main chart.\n\n' +
               'Ribbon lengths are fixed at 20, 50, 100, and 200.')
ma50Color  = input.color(color.new(#00a0dc, 5) , '', inline = 'RIB', group = maGR)
ma100Color = input.color(color.new(#0078be, 10), '', inline = 'RIB', group = maGR)
ma200Color = input.color(color.new(#005096, 15), '', inline = 'RIB', group = maGR)

stGR = 'Supertrend (Chart + Mini Charts)'
stLength = input.int(10, '  ATR Length', minval = 1, group = stGR, display = display)
stFactor = input.float(3, '  Factor', minval = 0.1, step = 0.1, group = stGR, display = display)
stColor = input.color(color.blue, '  Color', group = stGR)

group_rsi = 'RSI (Chart + Mini Charts)'
rsiLength = input.int(14, "  Length", minval = 1, group=group_rsi, display = display)
rsiSource = input.source(close, "  Source", group=group_rsi, display = display)
rsiSmoothing = input.bool(true, 'Signal Line       ', inline = 'RSI', group=group_rsi)
rsiMaType = input.string("EMA", "", options=["SMA", "EMA", "RMA", "WMA", "VWMA"], inline = 'RSI', group=group_rsi, display = display)
rsiMaLength = input.int(14, "  Signal Line Length", group=group_rsi, display = display)

group_stoch = 'Stochastic (Chart + Mini Charts)'
stochPeriodK = input.int(14, "  %K Length", minval=1, group=group_stoch, display = display)
stochSmoothK = input.int(1 , "  %K Smoothing", minval=1, group=group_stoch, display = display)
stochPeriodD = input.int(3 , "  %D Smoothing", minval=1, group=group_stoch, display = display)

group_vwcb = 'Volume-Weighted Candle Coloring (Chart + Mini Charts)'
vMaLen = input.int(89, '  Volume MA Length', group = group_vwcb, display = display,
     tooltip = 'Length of the moving average used to normalize volume activity.')
vwcbHigh = input.float(1.618, '  High Thresh', minval=1., step=.1, inline = 'H', group=group_vwcb, display = display)
vwHBLClr = input.color(#006400, '', inline = 'H', group = group_vwcb)
vwHBRClr = input.color(#910000, '', inline = 'H', group = group_vwcb)
vwcbLow = input.float(0.618, '  Low Thresh', minval=.1, step=.1, inline = 'L', group=group_vwcb, display = display) 
vwLBLClr = input.color(#7FFFD4, '', inline = 'L', group = group_vwcb)
vwLBRClr = input.color(#FF9800, '', inline = 'L', group = group_vwcb)

miscGR = 'Oscillator Layout (Chart + Mini Charts)'
oscVerticalOffset = input.int(9, "  Oscillator Offset", minval = 0, maxval = 17, group = miscGR, display = display,
     tooltip = 'Vertical offset of the oscillator relative to the price chart.\n\n' +
                 'Increase if the oscillator overlaps price.') / 10
oscHight = 11 - input.int(10, '  Oscillator Height' , minval = 1, maxval = 10 , group = miscGR, display = display,
     tooltip = 'Controls the vertical scaling of the oscillator display.')

//---------------------------------------------------------------------------------------------------------------------//
// User Defined Types

type htfCharts
	array<line> bars
    line    obLine
    line    midLine
    line    osLine
    line    refLine100
    line    refLine75
    line    refLine50
    line    refLine25
    line    refLine0

	array<chart.point> tiUpperPoints
	array<chart.point> tiBasisPoints
	array<chart.point> tiLowerPoints
	array<chart.point> oscPoints
	array<chart.point> sigPoints

	array<polyline> stLineHide
	polyline tiUpperLine
	polyline tiBasisLine
	polyline tiLowerLine
	polyline oscLine
	polyline sigLine

	array<label> stDirLabel
	label   panelTI
	label   panelOI
    label   refLabel100
    label   refLabel75
    label   refLabel50
    label   refLabel25
    label   refLabel0

//---------------------------------------------------------------------------------------------------------------------//
// Variables

noColor = #00000000

nzVolume = nz(volume)
vSMA = ta.sma(nzVolume, vMaLen)

//---------------------------------------------------------------------------------------------------------------------//
// Functions / Methods

timeframe(userTimeframe) =>
    float chartTFinM = timeframe.in_seconds() / 60

    switch 
        userTimeframe == '1 Minute' and chartTFinM <= 1 => '1'
        userTimeframe == '3 Minutes' and chartTFinM <= 3 => '3'
        userTimeframe == '5 Minutes' and chartTFinM <= 5 => '5'
        userTimeframe == '15 Minutes' and chartTFinM <= 15 => '15'
        userTimeframe == '30 Minutes' and chartTFinM <= 30 => '30'
        userTimeframe == '1 Hour' and chartTFinM <= 60 => '60'
        userTimeframe == '2 Hours' and chartTFinM <= 120 => '120'
        userTimeframe == '4 Hours' and chartTFinM <= 240 => '240'
        userTimeframe == '12 Hours' and chartTFinM <= 720 => '720'
        userTimeframe == '1 Day' and timeframe.isintraday => 'D'
        userTimeframe == '1 Week' and (timeframe.isdaily or timeframe.isintraday) => 'W'
        userTimeframe == '1 Month' and (timeframe.isweekly or timeframe.isdaily or timeframe.isintraday) => 'M'
        => timeframe.period

tfStringToMinutes(tfStr) =>
     tfStr == '1'   ? 1   :
     tfStr == '3'   ? 3   :
     tfStr == '5'   ? 5   :
     tfStr == '15'  ? 15  :
     tfStr == '30'  ? 30  :
     tfStr == '60'  ? 60  :
     tfStr == '120' ? 2 * 60 :
     tfStr == '240' ? 4 * 60 :
     tfStr == '720' ? 12 * 60 :
     tfStr == 'D'   ? 24 * 60 :
     tfStr == 'W'   ? 7  * 24 * 60 :
     tfStr == 'M'   ? 30 * 24 * 60 :
     timeframe.in_seconds() / 60

tfToBars(userTF) =>
    string effectiveTF = timeframe(userTF)
    float effectiveMinutes = tfStringToMinutes(effectiveTF)
    float chartMinutes = timeframe.in_seconds() / 60

    math.max(1, int(effectiveMinutes / chartMinutes))

lookbackBars = math.min(int(math.max(
     (htf1SHm ? htf1NB : 1) * (htf1SHm ? tfToBars(htf1TF) : 1), 
     (htf2SHm ? htf2NB : 1) * (htf2SHm ? tfToBars(htf2TF) : 1))), 15000)

oscHST = 100//ta.highest(osc, lookbackBars)

pLST = ta.lowest (low , math.max(lookbackBars, math.max(htf1NB, htf2NB)))
pHST = ta.highest(high, math.max(lookbackBars, math.max(htf1NB, htf2NB)))
pCHR = pHST != 0 ? (pHST - pLST) / pHST : 0

tiMaxLength = math.max(stLength, maLength, bbLength, rsiLength + rsiMaLength, stochPeriodK + stochSmoothK + stochPeriodD, vMaLen, 200)
lookbackBars := math.max(lookbackBars, math.max(htf1NB, htf2NB) + tiMaxLength + 1)

timeframeText(userTimeframe) =>
    tf = timeframe(userTimeframe)

    if not str.contains(tf, 'D') and not str.contains(tf, 'W') and not str.contains(tf, 'M') and not str.contains(tf, 'S')
        numTF = str.tonumber(tf)
        if numTF < 60
            tf + 'm'
        else
            str.tostring(numTF / 60) + 'H'
    else
        tf

movingAverage(source, length, maType) =>
    switch maType
        'SMA' => ta.sma(source, length)
        'EMA' => ta.ema(source, length)
        'HMA' => ta.hma(source, length)
        'RMA' => ta.rma(source, length)
        'WMA' => ta.wma(source, length)
        'VWMA' => ta.vwma(source, length)

bollingerBands(source, length, multiplier, maType) =>
    [movingAve
