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
    [movingAverage(source, length, maType), multiplier * ta.stdev(source, length)]

supertrend(factor, atrPeriod) =>
    ta.supertrend(factor, atrPeriod)

rsi() =>
    osc = ta.rsi(rsiSource, rsiLength)
    sig = rsiSmoothing ? movingAverage(osc, rsiMaLength, rsiMaType) : na

    stat = switch 
        osc > 70  => '▲ Overbought'
        osc >= 60 => '▲ Bullish'
        osc > 40  => 'Neutral'
        osc > 30  => '▼ Bearish'
        => '▼ Oversold'

    [osc, sig, '\nRSI(' + str.tostring(osc, '#.#') + ') · ' + stat]

stochastic() =>
    osc = movingAverage(ta.stoch(close, high, low, stochPeriodK), stochSmoothK, 'SMA') 
    sig = movingAverage(osc, stochPeriodD, 'SMA')

    stat = switch 
        osc > 80  => '▲ Overbought'
        osc >= 60 => '▲ Bullish'
        osc > 40  => 'Neutral'
        osc > 20  => '▼ Bearish'
        => '▼ Oversold'

    [osc, sig, '\nStochastic(' + str.tostring(osc, '#.#') + ') · ' +  stat]

volumeCandle(vol) =>
    volMa = ta.sma(vol, vMaLen)
    volState =
         vol > volMa * vwcbHigh ?  1 :
         vol < volMa * vwcbLow  ? -1 : 0
    [volMa, volState]

alarm(cond, message, htfUser, oncePerBarClose) =>
    if cond
        fullMessage = str.format("{0}\n{1} Price ({2}) Timeframe {3}", 
            message, syminfo.ticker, str.tostring(close, format.mintick), htfUser)
        alert(fullMessage, oncePerBarClose ? alert.freq_once_per_bar_close : alert.freq_once_per_bar)

collectData(collect, technicalIndicator, oscIndicator, numberOfBars, mini) =>

    var openArray = array.new_float()
    var highArray = array.new_float()
    var lowArray  = array.new_float()
    var closeArray = array.new_float()

    var float htfVOL = na
    var float htfVOLa = na
    var volumeStatArray = array.new_int()

    var tiBasisArray = array.new_float()
    var tiComponentArray = array.new_float()
    var tiHighArray = array.new_float()

    var oscArray = array.new_float()
    var sigArray = array.new_float()
    var string oscStat = na

    var float htfMA20  = na
    var float htfMA50  = na
    var float htfMA100 = na
    var float htfMA200 = na

    if collect
        openArray.unshift(open)
        highArray.unshift(high)
        lowArray.unshift(low)
        closeArray.unshift(close)

        [volMA, volState] = volumeCandle(nzVolume)
        htfVOL  := nzVolume
        htfVOLa := volMA
        volumeStatArray.unshift(volState)

        htfMA20  := movingAverage(maSource,  20, maType)
        htfMA50  := movingAverage(maSource,  50, maType)
        htfMA100 := movingAverage(maSource, 100, maType)
        htfMA200 := movingAverage(maSource, 200, maType)

        if mini
            [tiSource, tiComponent] = switch technicalIndicator
                'Supertrend' => supertrend(stFactor, stLength)
                'Bollinger Bands' => bollingerBands(bbSource, bbLength, bbMult, bbType)
                'Moving Average' => [movingAverage(maSource, maLength, maType), 1]
                => [close, close]

            if technicalIndicator == 'Bollinger Bands'
                tiHighArray.unshift(tiSource + tiComponent)
            else
                tiHighArray.unshift(tiSource)

            tiBasisArray.unshift(tiSource)
            tiComponentArray.unshift(tiComponent)

            [oscComponent, sigComponent, statComponent] = switch oscIndicator
                'RSI' => rsi()
                'Stochastic' => stochastic()
                => [close, close, '']
            oscStat := statComponent
            oscArray.unshift(oscComponent)
            sigArray.unshift(sigComponent)

        if closeArray.size() > (mini ? numberOfBars : 1)
            openArray.pop()
            highArray.pop()
            lowArray.pop()
            closeArray.pop()
            volumeStatArray.pop()

            if mini 
                tiBasisArray.pop()
                tiComponentArray.pop()
                tiHighArray.pop()
                oscArray.pop()
                sigArray.pop()

            [openArray, highArray, lowArray, closeArray, volumeStatArray, htfVOL, htfVOLa,
                 htfMA20, htfMA50, htfMA100, htfMA200,
                 math.max(highArray.max(), tiHighArray.max()), 
                 tiBasisArray, tiComponentArray, oscArray, sigArray, oscStat]
        else
            [openArray, highArray, lowArray, closeArray, volumeStatArray, htfVOL, htfVOLa,
                 htfMA20, htfMA50, htfMA100, htfMA200,
                 math.max(highArray.max(), tiHighArray.max()), 
                 tiBasisArray, tiComponentArray, oscArray, sigArray, oscStat]

processMini(htfSH, htfTF, chart, openArray, highArray, lowArray, closeArray, volumeStatArray, htfHST, tiBasisArray, tiComponentArray, technicalIndicator, oscArray, sigArray, oscIndicator, offset, first, numberOfBars, oscStat, htfRL, htfLB, htfBLClr, htfBRClr, htfVW) =>

    hOffset = first ? offset : htf1SHm ? htf1SZ + offset + htf1NB : offset

    if htfSH

        //var bool cAlertH = false
        //var bool cAlertL = false
        //var bool stAlert = false

        //if timeframe.change(timeframe(htfTF))
        //    cAlertH := true
        //    cAlertL := true
        //    stAlert := true

        var htfCharts htfChart = htfCharts.new(
             array.new<line>(na), line(na), line(na), line(na), line(na), line(na), line(na), line(na), line(na), 
             array.new<chart.point>(na), array.new<chart.point>(na), array.new<chart.point>(na), array.new<chart.point>(na), array.new<chart.point>(na),
             array.new<polyline>(na), polyline.new(na), polyline.new(na), polyline.new(na), polyline.new(na), polyline.new(na), 
             array.new<label>(na), label(na), label(na), label(na), label(na), label(na), label(na), label(na))

        if not na(closeArray) and closeArray.size() > 0

            if htfChart.bars.size() > 0
                for i = htfChart.bars.size() - 1 to 0  by 1
                    line.delete(htfChart.bars.shift())

            if htfChart.stLineHide.size() > 0
                for i = 0 to htfChart.stLineHide.size() - 1 by 1
                    polyline.delete(htfChart.stLineHide.shift())

            if technicalIndicator != 'None'
                htfChart.tiUpperPoints.clear()
                htfChart.tiUpperLine.delete()

                htfChart.tiBasisPoints.clear()
                htfChart.tiBasisLine.delete()

                htfChart.tiLowerPoints.clear()
                htfChart.tiLowerLine.delete()

            if oscIndicator != 'None'
                htfChart.oscPoints.clear()
                htfChart.oscLine.delete()

                htfChart.sigPoints.clear()
                htfChart.sigLine.delete()

                htfChart.obLine.delete()
                htfChart.midLine.delete()
                htfChart.osLine.delete()
            
            if htfRL == 'Range Extremes' or htfRL == 'Range Quartiles'
                htfChart.refLine100.delete()
                htfChart.refLine0.delete()

                htfChart.refLabel100.delete()
                htfChart.refLabel0.delete()

            if htfRL == 'Range Quartiles'
                htfChart.refLine75.delete()
                htfChart.refLine50.delete()
                htfChart.refLine25.delete()

                htfChart.refLabel75.delete()
                htfChart.refLabel50.delete()
                htfChart.refLabel25.delete()

            if htfChart.stDirLabel.size() > 0
                for i = 0 to htfChart.stDirLabel.size() - 1 by 1
                    label.delete(htfChart.stDirLabel.shift())
        
            for index = 0 to closeArray.size() - 1

                arrayIndex = closeArray.size() - index - 1
                barIndex = hOffset + bar_index + index
                bearCandle = openArray.get(arrayIndex) > closeArray.get(arrayIndex)
                barColor = chart == 'High-Low' ? color.blue : 
                             htfVW ? 
                                 volumeStatArray.get(arrayIndex) ==  1 ? bearCandle ? vwHBRClr : vwHBLClr : 
                                 volumeStatArray.get(arrayIndex) == -1 ? bearCandle ? vwLBRClr : vwLBLClr : 
                                 bearCandle ? htfBRClr : htfBLClr :
                             bearCandle ? htfBRClr : htfBLClr

                if chart != 'High-Low'
                    htfChart.bars.push(line.new(barIndex, openArray.get(arrayIndex), barIndex, closeArray.get(arrayIndex), xloc.bar_index, extend.none, barColor, line.style_solid, 3))

                htfChart.bars.push(line.new(barIndex, highArray.get(arrayIndex), barIndex, lowArray.get(arrayIndex), xloc.bar_index, extend.none, barColor, line.style_solid, chart == 'High-Low' ? 3 : 1))

                if technicalIndicator != 'None' and tiBasisArray.get(arrayIndex) > 0
                    if technicalIndicator == 'Supertrend'
                        htfChart.tiBasisPoints.push(chart.point.from_index(barIndex, tiBasisArray.get(arrayIndex)))
                    else if technicalIndicator == 'Bollinger Bands'
                        htfChart.tiUpperPoints.push(chart.point.from_index(barIndex, tiBasisArray.get(arrayIndex) + tiComponentArray.get(arrayIndex)))
                        htfChart.tiBasisPoints.push(chart.point.from_index(barIndex, tiBasisArray.get(arrayIndex)))
                        htfChart.tiLowerPoints.push(chart.point.from_index(barIndex, tiBasisArray.get(arrayIndex) - tiComponentArray.get(arrayIndex)))
                    else
                        htfChart.tiBasisPoints.push(chart.point.from_index(barIndex, tiBasisArray.get(arrayIndex)))

                if oscIndicator != 'None' and oscArray.get(arrayIndex) > 0
                    htfChart.oscPoints.push(chart.point.from_index(barIndex, pLST * (1 - pCHR * oscVerticalOffset) * (1 + oscArray.get(arrayIndex) / oscHST * pCHR / oscHight) ))
                    htfChart.sigPoints.push(chart.point.from_index(barIndex, pLST * (1 - pCHR * oscVerticalOffset) * (1 + sigArray.get(arrayIndex) / oscHST * pCHR / oscHight) ))

                    //label.new(barIndex, high, str.tostring( pLST  * (1 - pCHR * oscVerticalOffset) * (1 + sigArray.get(arrayIndex) / oscHST * pCHR / oscHight) ))

            if technicalIndicator != 'None'

                if technicalIndicator == 'Supertrend'
                    htfChart.tiBasisLine := polyline.new(htfChart.tiBasisPoints, false, false, xloc.bar_index, stColor, noColor, line.style_solid, 1)

                    for index = 0 to closeArray.size() - 1 by 1
                        arrayIndex = closeArray.size() - index - 1
                        barIndex = hOffset + bar_index + index

                        if arrayIndex < closeArray.size() - 1
                            if tiComponentArray.get(arrayIndex) != tiComponentArray.get(arrayIndex + 1)

                                htfChart.stLineHide.push(polyline.new(array.from(chart.point.from_index(barIndex - 1, tiBasisArray.get(arrayIndex + 1)), chart.point.from_index(barIndex, tiBasisArray.get(arrayIndex))), false, false, xloc.bar_index, chart.bg_color, noColor, line.style_solid, 2))
                                htfChart.stDirLabel.push(label.new(barIndex, tiBasisArray.get(arrayIndex), '', color = stColor, style = label.style_circle, size = size.auto))
                                
                    //if tiComponentArray.first() != tiComponentArray.get(1) and stAlert
                    //    alarm(true, 'Supertrend Switch Direction', timeframeText(htfTF), true)
                    //    stAlert := false

                else if technicalIndicator == 'Bollinger Bands'
                    htfChart.tiUpperLine := polyline.new(htfChart.tiUpperPoints, false, false, xloc.bar_index, bbuColor, noColor, line.style_solid, 1)
                    htfChart.tiBasisLine := polyline.new(htfChart.tiBasisPoints, false, false, xloc.bar_index, bbbColor, noColor, line.style_solid, 1)
                    htfChart.tiLowerLine := polyline.new(htfChart.tiLowerPoints, false, false, xloc.bar_index, bbuColor, noColor, line.style_solid, 1)
                    htfChart.tiLowerLine
                else
                    htfChart.tiBasisLine := polyline.new(htfChart.tiBasisPoints, false, false, xloc.bar_index, maColor, noColor, line.style_solid, 1)
                    htfChart.tiBasisLine

            if oscIndicator != 'None'

                [oscColor, sigColor, upperBand, lowerBand] = if oscIndicator == 'RSI'
                    [#7e57c2, #fdd835, 70, 30]
                else
                    [#2962FF, #FF6D00, 80, 20]

                htfChart.oscLine := polyline.new(htfChart.oscPoints, false, false, xloc.bar_index, oscColor, noColor, line.style_solid, 1)
                htfChart.sigLine := polyline.new(htfChart.sigPoints, false, false, xloc.bar_index, sigColor, noColor, line.style_solid, 1)
                htfChart.obLine  := line.new(htfChart.oscPoints.first().index, pLST * (1 - pCHR * oscVerticalOffset) * (1 + upperBand / oscHST * pCHR / oscHight), htfChart.oscPoints.last().index, pLST * (1 - pCHR * oscVerticalOffset) * (1 + upperBand / oscHST * pCHR / oscHight), xloc.bar_index, extend.none, color.new(color.red , 50), line.style_solid , 2)
                htfChart.midLine := line.new(htfChart.oscPoints.first().index, pLST * (1 - pCHR * oscVerticalOffset) * (1 + 50        / oscHST * pCHR / oscHight), htfChart.oscPoints.last().index, pLST * (1 - pCHR * oscVerticalOffset) * (1 +        50 / oscHST * pCHR / oscHight), xloc.bar_index, extend.none, color.new(color.gray, 50), line.style_dotted, 2)
                htfChart.osLine  := line.new(htfChart.oscPoints.first().index, pLST * (1 - pCHR * oscVerticalOffset) * (1 + lowerBand / oscHST * pCHR / oscHight), htfChart.oscPoints.last().index, pLST * (1 - pCHR * oscVerticalOffset) * (1 + lowerBand / oscHST * pCHR / oscHight), xloc.bar_index, extend.none, color.new(color.teal, 50), line.style_solid , 2)

            if htfRL == 'Range Extremes' or htfRL == 'Range Quartiles'
                sIdx = bar_index[math.min(tfToBars(htfTF) * (numberOfBars - 1), 5000)]
                eIdx = hOffset + bar_index + numberOfBars

                hst = highArray.max()
                htfChart.refLine100  := line.new(sIdx, hst, eIdx, hst, xloc.bar_index, extend.none, color.new(color.gray , 50), line.style_solid, 1)
                    
                lst = lowArray.min()
                htfChart.refLine0  := line.new(sIdx, lst , eIdx, lst , xloc.bar_index, extend.none, color.new(color.gray , 50), line.style_solid, 1)
                    
                if htfLB
                    htfChart.refLabel100 := label.new(eIdx - 1, hst, 'H · ' + str.tostring(hst, format.mintick), color = noColor, style = label.style_label_lower_left, textcolor = chart.fg_color, size = size.small)
                    htfChart.refLabel0   := label.new(eIdx - 1, lst, 'L · ' + str.tostring(lst, format.mintick), color = noColor, style = label.style_label_upper_left, textcolor = chart.fg_color, size = size.small)

                if htfRL == 'Range Quartiles'
                    qRange = (hst - lst) / 4
                    htfChart.refLine75  := line.new(sIdx, lst + 3 * qRange, eIdx, lst + 3 * qRange, xloc.bar_index, extend.none, color.new(color.gray , 50), line.style_dashed, 1)
                    htfChart.refLine50  := line.new(sIdx, lst + 2 * qRange, eIdx, lst + 2 * qRange, xloc.bar_index, extend.none, color.new(color.gray , 50), line.style_dotted, 1)
                    htfChart.refLine25  := line.new(sIdx, lst + 1 * qRange, eIdx, lst + 1 * qRange, xloc.bar_index, extend.none, color.new(color.gray , 50), line.style_dashed, 1)
                        
                    if htfLB
                        htfChart.refLabel75 := label.new(eIdx, lst + 3 * qRange, '75% · ' + str.tostring(lst + 3 * qRange, format.mintick), color = noColor, style = label.style_label_left, textcolor = chart.fg_color, size = size.small)
                        htfChart.refLabel50 := label.new(eIdx, lst + 2 * qRange, '50% · ' + str.tostring(lst + 2 * qRange, format.mintick), color = noColor, style = label.style_label_left, textcolor = chart.fg_color, size = size.small)
                        htfChart.refLabel25 := label.new(eIdx, lst + 1 * qRange, '25% · ' + str.tostring(lst + 1 * qRange, format.mintick), color = noColor, style = label.style_label_left, textcolor = chart.fg_color, size = size.small)

            if htfLB
                //volStt = volumeStatArray.first() ==  1 ? '\nParticipation · High'  : 
                //           volumeStatArray.first() == -1 ? '\nParticipation · Low' : '\nParticipation · Normal'
                panelTextTI = timeframeText(htfTF) + ' · ' + chart + (technicalIndicator != 'None' ? technicalIndicator == 'Moving Average' ? '\n' + technicalIndicator + ' (' + maType + ')' : '\n' + technicalIndicator : '') //+ volStt
                htfChart.panelTI.delete()
                htfChart.panelTI := label.new(hOffset + int(numberOfBars / 2) + bar_index, htfHST, panelTextTI, color = noColor, style = label.style_label_down, textcolor = chart.fg_color, textalign = text.align_left)
                htfChart.panelTI

                if oscIndicator != 'None'
                    panelTextOI = oscStat
                    htfChart.panelOI.delete()
                    htfChart.panelOI := label.new(hOffset + int(numberOfBars / 2) + bar_index, pLST * (1 - pCHR * oscVerticalOffset), panelTextOI, color = noColor, style = label.style_label_up, textcolor = chart.fg_color, textalign = text.align_left)
                    htfChart.panelOI

            //if cAlertH
            //    alarm(highArray.first() > highArray.max(1) and true, 'New High Detected among last ' + str.tostring(numberOfBars) + ' HTF(' + timeframeText(htfTF) + ') candles', timeframeText(htfTF), false)
            //    cAlertH := false
            //if cAlertL
            //    alarm(lowArray.first()  < lowArray.min(1)  and true, 'New Low Detected among last '  + str.tostring(numberOfBars) + ' HTF(' + timeframeText(htfTF) + ') candles', timeframeText(htfTF), false)
            //    cAlertL := false

processHTF(htfTF, htfCT, openArray, highArray, lowArray, closeArray, volumeStatArray, htfBLClr, htfBRClr, htfClrT, htfVW) =>

    var box htfBXhl = na
    var box htfBXoc = na


    if not na(closeArray) and closeArray.size() > 0
        bearCandle = closeArray.first() < openArray.first()
        bxColor = htfVW ? 
                     volumeStatArray.first() ==  1 ? bearCandle ? vwHBRClr : vwHBLClr : 
                     volumeStatArray.first() == -1 ? bearCandle ? vwLBRClr : vwLBLClr : 
                             bearCandle ? htfBRClr : htfBLClr :
                             bearCandle ? htfBRClr : htfBLClr

        if timeframe.change(timeframe(htfTF))
            htfBXhl := box.new(bar_index, highArray.first(), bar_index, lowArray.first(), color.new(bxColor, 70), bgcolor = color.new(bxColor, htfClrT))

            if htf1CT != 'High-Low'
                htfBXoc := box.new(bar_index, openArray.first(), bar_index, closeArray.first(), color.new(bxColor, 70), bgcolor = color.new(bxColor, htfClrT))
            true
        else
            htfBXhl.set_top(highArray.first())
            htfBXhl.set_rightbottom(bar_index, lowArray.first())
            htfBXhl.set_bgcolor(color.new(bxColor, htfClrT))
            htfBXhl.set_border_color(color.new(bxColor, 70))

            if htfCT != 'High-Low'
                htfBXoc.set_top(openArray.first()) // test
                htfBXoc.set_rightbottom(bar_index, closeArray.first())
                htfBXoc.set_bgcolor(color.new(bxColor, htfClrT))
                htfBXoc.set_border_color(color.new(bxColor, 70))
            true

//---------------------------------------------------------------------------------------------------------------------//
// Calculations

htf1SY = htf1CT == 'Heikin Ashi' ? ticker.heikinashi(syminfo.tickerid) : ticker.standard(syminfo.tickerid)
[openArray1, highArray1, lowArray1, closeArray1, volumeStatArray1, htfVOL1, htfVOLa1, htfMA201, htfMA501, htfMA1001, htfMA2001, htfHST1, tiBasisArray1, tiComponentArray1, oscArray1, sigArray1, oscStat1] = 
     request.security(htf1SY, timeframe(htf1TF), collectData(htf1SH or htf1SHm or volStat or pmaStat, htf1TI, htf1OI, htf1NB, htf1SHm), calc_bars_count = lookbackBars + 1)

htf2SY = htf2CT == 'Heikin Ashi' ? ticker.heikinashi(syminfo.tickerid) : ticker.standard(syminfo.tickerid)
[openArray2, highArray2, lowArray2, closeArray2, volumeStatArray2, htfVOL2, htfVOLa2, htfMA202, htfMA502, htfMA1002, htfMA2002, htfHST2, tiBasisArray2, tiComponentArray2, oscArray2, sigArray2, oscStat2] = 
     request.security(htf2SY, timeframe(htf2TF), collectData(htf2SH or htf2SHm or volStat or pmaStat, htf2TI, htf2OI, htf2NB, htf2SHm), calc_bars_count = lookbackBars + 1)

processMini((chart.is_standard or chart.is_heikinashi) and htf1SHm and barstate.islast and last_bar_index > math.max(htf1NB, htf2NB) + tiMaxLength - 1, htf1TF, htf1CT, openArray1, highArray1, lowArray1, closeArray1, volumeStatArray1, htfHST1, tiBasisArray1, tiComponentArray1, htf1TI, oscArray1, sigArray1, htf1OI, htf1SZ, true , htf1NB, oscStat1, htf1RL, htf1LB, htf1BLClr, htf1BRClr, htf1VWm)
processMini((chart.is_standard or chart.is_heikinashi) and htf2SHm and barstate.islast and last_bar_index > math.max(htf1NB, htf2NB) + tiMaxLength - 1, htf2TF, htf2CT, openArray2, highArray2, lowArray2, closeArray2, volumeStatArray2, htfHST2, tiBasisArray2, tiComponentArray2, htf2TI, oscArray2, sigArray2, htf2OI, htf2SZ, false, htf2NB, oscStat2, htf2RL, htf2LB, htf2BLClr, htf2BRClr, htf2VWm)

if htf1SH
    processHTF(htf1TF, htf1CT, openArray1, highArray1, lowArray1, closeArray1, volumeStatArray1, htf1BLClr, htf1BRClr, htf1ClrT, htf1VW)

if htf2SH
    processHTF(htf2TF, htf2CT, openArray2, highArray2, lowArray2, closeArray2, volumeStatArray2, htf2BLClr, htf2BRClr, htf2ClrT, htf2VW)

//plot(htfMA201)

[supertrend, direction] = ta.supertrend(stFactor, stLength)

supertrend := barstate.isfirst ? na : supertrend
upTrend =    plot(chartTI == 'Supertrend' ? direction < 0 ? supertrend : na : na, "ST Up Trend",   color = color.green, style = plot.style_linebr, display = display)
downTrend =  plot(chartTI == 'Supertrend' ? direction < 0 ? na : supertrend : na, "ST Down Trend", color = color.red,   style = plot.style_linebr, display = display)
bodyMiddle = plot(chartTI == 'Supertrend' ? barstate.isfirst ? na : (open + close) / 2 : na, "Body Middle", display = display.none, editable = false)

fill(bodyMiddle, upTrend,   title = "ST Uptrend Fill",   color = color.new(color.green, 90), fillgaps = false)
fill(bodyMiddle, downTrend, title = "ST Downtrend Fill", color = color.new(color.red,   90), fillgaps = false)

[basis, dev] = bollingerBands(bbSource, bbLength, bbMult, bbType)

plot(chartTI == 'Bollinger Bands' ? basis : na, "BB Basis", color=bbbColor, display = display)
p1 = plot(chartTI == 'Bollinger Bands' ? basis + dev : na, "BB Upper", color=bbuColor, display = display)
p2 = plot(chartTI == 'Bollinger Bands' ? basis - dev : na, "BB Lower", color=bbuColor, display = display)

ma20  = movingAverage(maSource, 20, maType)
ma50  = movingAverage(maSource, 50, maType)
ma100 = movingAverage(maSource, 100, maType)
ma200 = movingAverage(maSource, 200, maType)

plot(chartTI == 'Moving Average Ribbon' ? ma20   : na, 'MA (20)' , ma20Color , 1, display = display)
plot(chartTI == 'Moving Average Ribbon' ? ma50   : na, 'MA (50)' , ma50Color , 1, display = display)
plot(chartTI == 'Moving Average Ribbon' ? ma100  : na, 'MA (100)', ma100Color, 2, display = display)
plot(chartTI == 'Moving Average Ribbon' ? ma200  : na, 'MA (200)', ma200Color, 2, display = display)


var a_lines = array.new_line()
var polyline oscLineC = na
var polyline sigLineC = na
var label oiLabel = na

oscPointsC = array.new<chart.point>(0)
sigPointsC = array.new<chart.point>(0)

lookbackLength = math.max(htf1NB, htf2NB)

[osc, sig, stat] = switch chartOI
    'RSI' => rsi()
    'Stochastic' => stochastic()

[oscColor, sigColor, upperBand, lowerBand] = if chartOI == 'RSI'
    [#7e57c2, #fdd835, 70, 30]
else
    [#2962FF, #FF6D00, 80, 20]

if barstate.islast and chartOI != 'None'

    if array.size(a_lines) > 0
        for i = 1 to array.size(a_lines)
            line.delete(array.shift(a_lines))

    oscLineC.delete()
    sigLineC.delete()
    oiLabel.delete()

    a_lines.push(line.new(bar_index[lookbackLength], pLST * (1 - pCHR * oscVerticalOffset) * (1 + upperBand / oscHST * pCHR / oscHight), bar_index, pLST * (1 - pCHR * oscVerticalOffset) * (1 + upperBand / oscHST * pCHR / oscHight), xloc.bar_index, extend.none, color.new(color.red , 50), line.style_solid , 2))
    a_lines.push(line.new(bar_index[lookbackLength], pLST * (1 - pCHR * oscVerticalOffset) * (1 + 50        / oscHST * pCHR / oscHight), bar_index, pLST * (1 - pCHR * oscVerticalOffset) * (1 +        50 / oscHST * pCHR / oscHight), xloc.bar_index, extend.none, color.new(color.gray, 50), line.style_dotted, 2))
    a_lines.push(line.new(bar_index[lookbackLength], pLST * (1 - pCHR * oscVerticalOffset) * (1 + lowerBand / oscHST * pCHR / oscHight), bar_index, pLST * (1 - pCHR * oscVerticalOffset) * (1 + lowerBand / oscHST * pCHR / oscHight), xloc.bar_index, extend.none, color.new(color.teal, 50), line.style_solid , 2))

    oiLabel := label.new(bar_index[int(math.max(htf1NB, htf2NB)/2)], pLST * (1 - pCHR * oscVerticalOffset), stat, color = noColor, style = label.style_label_up, textcolor = chart.fg_color, textalign = text.align_left)

    for barIndex = 0 to lookbackLength - 1

        if osc[barIndex] > 0
            oscPointsC.push(chart.point.from_index(bar_index[barIndex], pLST * (1 - pCHR * oscVerticalOffset) * (1 + osc[barIndex] / oscHST * pCHR / oscHight)))

        if rsiSmoothing
            sigPointsC.push(chart.point.from_index(bar_index[barIndex], pLST * (1 - pCHR * oscVerticalOffset) * (1 + sig[barIndex] / oscHST * pCHR / oscHight)))

    oscLineC := polyline.new(oscPointsC, line_color = oscColor)
    sigLineC := polyline.new(sigPointsC, line_color = sigColor)

//---------------------------------------------------------------------------------------------------------------------//

//---------------------------------------------------------------------------------------------------------------------//
// Volume-Weighted Candle

bullCandle    = close > open
barcolor(chartVW and bool(nzVolume) ?
        nzVolume > vSMA * vwcbHigh ?
            bullCandle ? vwHBLClr : vwHBRClr :
        nzVolume < vSMA * vwcbLow ?
            bullCandle ? vwLBLClr : vwLBRClr : na
    : na, title='Volume Weighted Colored Bars', editable = false)

//alarm(nzVolume > vSMA * vwcbHigh, 'High trading Volume detected', timeframe.period, false)
//alarm(nzVolume > vSMA * 4.669, 'Watch out, Volume SPIKE detected, may be a sign of exhaustion', timeframe.period, false)

//---------------------------------------------------------------------------------------------------------------------//
// Statistical Panel

//var float firstC = na
//if barstate.isfirst
//    firstC := close

getPriceValue(htf) =>
    var value = 0.
    if timeframe.change(htf)
        value := close[1]
    value
    
dROR = (close / getPriceValue('D')   - 1) * 100
wROR = (close / getPriceValue('W')   - 1) * 100
mROR = (close / getPriceValue('M')   - 1) * 100
qROR = (close / getPriceValue('3M')  - 1) * 100
yROR = (close / getPriceValue('12M') - 1) * 100

//if na(yROR)
//    yROR := (close / firstC - 1) * 100

var float q1 = na, var float q2 = na, var float q3 = na, var float q4 = na

if month < 4
    q1 := qROR, q2 := na, q3 := na, q4 := na
else if month > 3 and month < 7
    q2 := qROR
else if month > 6 and month < 10
    q3 := qROR
else if month > 9
    q4 := qROR

var float yROR1 = na, var float yROR2 = na, var float yROR3 = na
var int yr1 = na, var int yr2 = na, var int yr3= na

if timeframe.change('12M')
    yROR3 := yROR2  , yr3 := yr2
    yROR2 := yROR1  , yr2 := yr1
    yROR1 := yROR[1], yr1 := year[1]

upColor = #22ab94
dnColor = #f23645
naColor = #9aa0a6
transp  = 89

var table change = table.new(position.top_right, 4, 10, border_width=3)

if barstate.islast and chgStat and chart.is_standard
    //table.cell(change, 0, 0, 'Perf', text_color=naColor, bgcolor=color.new(naColor, 81), text_halign=text.align_left, text_size=textSize,text_font_family = font.family_monospace)

    if not timeframe.isweekly and not timeframe.ismonthly and not na(dROR)
        table.cell(change, 1, 0, str.tostring( dROR, '#.##')  + '%\nDTD' , text_color=dROR > 0  ? upColor : dnColor, bgcolor=dROR > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip='Day to Date', text_font_family = font.family_monospace)
        if not timeframe.ismonthly
            table.cell(change, 2, 0, na(wROR) ? '-\nWTD' : str.tostring( wROR, '#.##')  + '%\nWTD' , text_color=na(wROR) ? naColor : wROR > 0  ? upColor : dnColor, bgcolor=na(wROR) ? color.new(naColor, transp) : wROR > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip='Week to Date' , text_font_family = font.family_monospace)
        table.cell    (change, 3, 0, na(mROR) ? '-\nMTD' : str.tostring( mROR, '#.##')  + '%\nMTD' , text_color=na(mROR) ? naColor : mROR > 0  ? upColor : dnColor, bgcolor=na(mROR) ? color.new(naColor, transp) : mROR > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip='Month to Date', text_font_family = font.family_monospace)

    if not na(q1) //and not na(q2) and not na(q3) and not na(q4)
        table.cell(change, 0, 1, na(q1) ? '-\nQ1' : str.tostring( q1, '#.##') + '%\nQ1', text_color=na(q1) ? naColor : q1 > 0 ? upColor : dnColor, bgcolor=na(q1) ? color.new(naColor, transp) : q1 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip='1st Quarter of ' + str.tostring(year), text_font_family = font.family_monospace)
        table.cell(change, 1, 1, na(q2) ? '-\nQ2' : str.tostring( q2, '#.##') + '%\nQ2', text_color=na(q2) ? naColor : q2 > 0 ? upColor : dnColor, bgcolor=na(q2) ? color.new(naColor, transp) : q2 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip='2nd Quarter of ' + str.tostring(year), text_font_family = font.family_monospace)
        table.cell(change, 2, 1, na(q3) ? '-\nQ3' : str.tostring( q3, '#.##') + '%\nQ3', text_color=na(q3) ? naColor : q3 > 0 ? upColor : dnColor, bgcolor=na(q3) ? color.new(naColor, transp) : q3 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip='3rd Quarter of ' + str.tostring(year), text_font_family = font.family_monospace)
        table.cell(change, 3, 1, na(q4) ? '-\nQ4' : str.tostring( q4, '#.##') + '%\nQ4', text_color=na(q4) ? naColor : q4 > 0 ? upColor : dnColor, bgcolor=na(q4) ? color.new(naColor, transp) : q4 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip='4th Quarter of ' + str.tostring(year), text_font_family = font.family_monospace)

    if not na(yROR)
        table.cell(change, 3, 2, str.tostring(yROR , '#.##') + '%\n' + str.tostring(year), text_color=yROR  > 0 ? upColor : dnColor, bgcolor=yROR  > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip= str.tostring(year) + ' Year to Date', text_font_family = font.family_monospace)
        table.cell(change, 2, 2, na(yROR1) ? '-\n-' : str.tostring(yROR1, '#.##') + '%\n' + str.tostring(yr1) , text_color=na(yROR1) ? naColor : yROR1 > 0 ? upColor : dnColor, bgcolor=na(yROR1) ? color.new(naColor, transp) : yROR1 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip=na(yROR1) and na(yr1) ? '' : str.tostring(yr1) + ' Rate of Return', text_font_family = font.family_monospace)
        table.cell(change, 1, 2, na(yROR2) ? '-\n-' : str.tostring(yROR2, '#.##') + '%\n' + str.tostring(yr2) , text_color=na(yROR2) ? naColor : yROR2 > 0 ? upColor : dnColor, bgcolor=na(yROR2) ? color.new(naColor, transp) : yROR2 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip=na(yROR2) and na(yr2) ? '' : str.tostring(yr2) + ' Rate of Return', text_font_family = font.family_monospace)
        table.cell(change, 0, 2, na(yROR3) ? '-\n-' : str.tostring(yROR3, '#.##') + '%\n' + str.tostring(yr3) , text_color=na(yROR3) ? naColor : yROR3 > 0 ? upColor : dnColor, bgcolor=na(yROR3) ? color.new(naColor, transp) : yROR3 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, tooltip=na(yROR3) and na(yr3) ? '' : str.tostring(yr3) + ' Rate of Return', text_font_family = font.family_monospace)

pma(ma) =>
    (close / ma - 1) * 100

if barstate.islast and pmaStat and chart.is_standard
    table.cell(change, 1, 3, 'Chart'   , text_color=naColor, bgcolor=color.new(naColor, 81), text_size=textSize,text_font_family = font.family_monospace)
    table.cell(change, 2, 3, timeframeText(htf1TF) , text_color=naColor, bgcolor=color.new(naColor, 81), text_size=textSize,text_font_family = font.family_monospace)
    table.cell(change, 3, 3, timeframeText(htf2TF), text_color=naColor, bgcolor=color.new(naColor, 81), text_size=textSize,text_font_family = font.family_monospace)

    pma20c = pma(ma20), pma201 = pma(htfMA201), pma202  = pma(htfMA202)
    table.cell(change, 0, 4, 'MA20', text_color=naColor, bgcolor=color.new(naColor, 81), text_halign=text.align_left, text_size=textSize, text_font_family = font.family_monospace)
    table.cell(change, 1, 4, na(pma20c) ? '-' : str.tostring(pma20c, '#.##') + '%', text_color = na(pma20c) ? naColor : pma20c > 0 ? upColor : dnColor, bgcolor=na(pma20c) ? color.new(naColor, transp) : pma20c > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
    table.cell(change, 2, 4, na(pma201) ? '-' : str.tostring(pma201, '#.##') + '%', text_color = na(pma201) ? naColor : pma201 > 0 ? upColor : dnColor, bgcolor=na(pma201) ? color.new(naColor, transp) : pma201 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
    table.cell(change, 3, 4, na(pma202) ? '-' : str.tostring(pma202, '#.##') + '%', text_color = na(pma202) ? naColor : pma202 > 0 ? upColor : dnColor, bgcolor=na(pma202) ? color.new(naColor, transp) : pma202 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)

    pma50c = pma(ma50), pma501 = pma(htfMA501), pma502  = pma(htfMA502)
    if not na(pma50c)
        table.cell(change, 0, 5, 'MA50', text_color=naColor, bgcolor=color.new(naColor, 81), text_halign=text.align_left, text_size=textSize,text_font_family = font.family_monospace)
        table.cell(change, 1, 5, na(pma50c) ? '-' : str.tostring(pma50c, '#.##') + '%', text_color = na(pma50c) ? naColor : pma50c > 0 ? upColor : dnColor, bgcolor=na(pma50c) ? color.new(naColor, transp) : pma50c > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 2, 5, na(pma501) ? '-' : str.tostring(pma501, '#.##') + '%', text_color = na(pma501) ? naColor : pma501 > 0 ? upColor : dnColor, bgcolor=na(pma501) ? color.new(naColor, transp) : pma501 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 3, 5, na(pma502) ? '-' : str.tostring(pma502, '#.##') + '%', text_color = na(pma502) ? naColor : pma502 > 0 ? upColor : dnColor, bgcolor=na(pma502) ? color.new(naColor, transp) : pma502 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)

    pma100c = pma(ma100), pma1001 = pma(htfMA1001), pma1002  = pma(htfMA1002)
    if not na(pma100c)
        table.cell(change, 0, 6, 'MA100', text_color=naColor, bgcolor=color.new(naColor, 81), text_halign=text.align_left, text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 1, 6, na(pma100c) ? '-' : str.tostring(pma100c, '#.##') + '%', text_color = na(pma100c) ? naColor : pma100c > 0 ? upColor : dnColor, bgcolor=na(pma100c) ? color.new(naColor, transp) : pma100c > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 2, 6, na(pma1001) ? '-' : str.tostring(pma1001, '#.##') + '%', text_color = na(pma1001) ? naColor : pma1001 > 0 ? upColor : dnColor, bgcolor=na(pma1001) ? color.new(naColor, transp) : pma1001 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 3, 6, na(pma1002) ? '-' : str.tostring(pma1002, '#.##') + '%', text_color = na(pma1002) ? naColor : pma1002 > 0 ? upColor : dnColor, bgcolor=na(pma1002) ? color.new(naColor, transp) : pma1002 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)

    pma200c = pma(ma200), pma2001 = pma(htfMA2001), pma2002  = pma(htfMA2002)
    if not na(pma200c)
        table.cell(change, 0, 7, 'MA200', text_color=naColor, bgcolor=color.new(naColor, 81), text_halign=text.align_left, text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 1, 7, na(pma200c) ? '-' : str.tostring(pma200c, '#.##') + '%', text_color=na(pma200c) ? naColor : pma200c > 0 ? upColor : dnColor, bgcolor=na(pma200c) ? color.new(naColor, transp) : pma200c > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 2, 7, na(pma2001) ? '-' : str.tostring(pma2001, '#.##') + '%', text_color=na(pma2001) ? naColor : pma2001 > 0 ? upColor : dnColor, bgcolor=na(pma2001) ? color.new(naColor, transp) : pma2001 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)
        table.cell(change, 3, 7, na(pma2002) ? '-' : str.tostring(pma2002, '#.##') + '%', text_color=na(pma2002) ? naColor : pma2002 > 0 ? upColor : dnColor, bgcolor=na(pma2002) ? color.new(naColor, transp) : pma2002 > 0 ? color.new(upColor, transp) : color.new(dnColor, transp), text_size=textSize, text_font_family = font.family_monospace)

if barstate.islast and volStat
    table.cell(change, 1, 8, 'Chart'  , text_color=naColor, bgcolor=color.new(naColor, 81), text_size=textSize, text_font_family = font.family_monospace)
    table.cell(change, 2, 8, timeframeText(htf1TF), text_color=naColor, bgcolor=color.new(naColor, 81), text_size=textSize, text_font_family = font.family_monospace)
    table.cell(change, 3, 8, timeframeText(htf2TF), text_color=naColor, bgcolor=color.new(naColor, 81), text_size=textSize, text_font_family = font.family_monospace)

    table.cell(change, 0, 9, 'VOLUME\nAVG(' + str.tostring(vMaLen) + ')', text_color=naColor, bgcolor=color.new(naColor, 81), text_halign=text.align_left, text_size=textSize, text_font_family = font.family_monospace)
    table.cell(change, 1, 9, str.tostring(nzVolume, format.volume) + '\n' + (na(vSMA)     ? '-' : str.tostring(vSMA    , format.volume)), text_color = nzVolume > vSMA     ? upColor : naColor, bgcolor = nzVolume > vSMA    ? color.new(upColor, transp) : color.new(naColor, transp), text_size=textSize, text_font_family = font.family_monospace)
    
    table.cell(change, 2, 9, (na(htfVOL1) ? '-' : str.tostring(htfVOL1 , format.volume)) + '\n' + (na(htfVOLa1) ? '-' : str.tostring(htfVOLa1, format.volume)), text_color = htfVOL1 > htfVOLa1  ? upColor : naColor, bgcolor = htfVOL1 > htfVOLa1 ? color.new(upColor, transp) : color.new(naColor, transp), text_size=textSize, text_font_family = font.family_monospace)
    table.cell(change, 3, 9, (na(htfVOL2) ? '-' : str.tostring(htfVOL2 , format.volume)) + '\n' + (na(htfVOLa2) ? '-' : str.tostring(htfVOLa2, format.volume)), text_color = htfVOL2 > htfVOLa2  ? upColor : naColor, bgcolor = htfVOL2 > htfVOLa2 ? color.new(upColor, transp) : color.new(naColor, transp), text_size=textSize, text_font_family = font.family_monospace)

//---------------------------------------------------------------------------------------------------------------------//

var table logo = table.new(position.bottom_right, 1, 1)
if barstate.islast
    table.cell(logo, 0, 0, '☼☾  ', text_size = size.normal, text_color = color.teal, tooltip = 'SoleMare Analytics')
