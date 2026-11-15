//@version=6
indicator("3 Mini Charts + Stochastic", "3 Mini Stoch", overlay=true, max_lines_count=500, max_polylines_count=20, scale=scale.none, dynamic_requests=true)


// ─── Mini Chart Layout ───
miniGroup = "Mini Chart Layout"

barsToShow = input.int(35, "Candles to Show", minval=10, maxval=45, group=miniGroup)
xOffset = input.int(5, "Horizontal Offset", minval=0, maxval=50, group=miniGroup)
verticalSpacing = input.float(1.12, "Vertical Spacing", minval=0.5, maxval=3.0, step=0.05, group=miniGroup)

topPosition = input.float(2.24, "Top Vertical Position", minval=0.0, maxval=10.0, step=0.1, group=miniGroup)
midPosition = input.float(1.12, "Middle Vertical Position", minval=0.0, maxval=10.0, step=0.1, group=miniGroup)
botPosition = input.float(0.0, "Bottom Vertical Position", minval=0.0, maxval=10.0, step=0.1, group=miniGroup)

showCandles = input.bool(true, "Show Candles", group=miniGroup)
showTop = input.bool(true, "Show Top Chart", group=miniGroup)
showMiddle = input.bool(true, "Show Middle Chart", group=miniGroup)
showBottom = input.bool(true, "Show Bottom Chart", group=miniGroup)

topChartTF = input.string("Chart", "Top Chart Timeframe", options=["Chart", "5 Minutes", "15 Minutes", "1 Hour", "4 Hours", "1 Day", "1 Week", "1 Month"], group=miniGroup)
midChartTF = input.string("Chart", "Middle Chart Timeframe", options=["Chart", "5 Minutes", "15 Minutes", "1 Hour", "4 Hours", "1 Day", "1 Week", "1 Month"], group=miniGroup)
botChartTF = input.string("Chart", "Bottom Chart Timeframe", options=["Chart", "5 Minutes", "15 Minutes", "1 Hour", "4 Hours", "1 Day", "1 Week", "1 Month"], group=miniGroup)

// ─── Top Stochastic ───
topGR = "Top Stochastic"
topKLen = input.int(14, "%K Length", minval=1, group=topGR)
topKSmooth = input.int(3, "%K Smoothing", minval=1, group=topGR)
topDSmooth = input.int(3, "%D Smoothing", minval=1, group=topGR)
topStochTF = input.string("Chart", "Stochastic Timeframe", options=["Chart", "5 Minutes", "15 Minutes", "1 Hour", "4 Hours", "1 Day", "1 Week", "1 Month"], group=topGR)
topWait = input.bool(true, "Wait for Timeframe Close", group=topGR)
topKColor = input.color(color.aqua, "%K Color", group=topGR)
topDColor = input.color(color.orange, "%D Color", group=topGR)

// ─── Middle Stochastic ───
midGR = "Middle Stochastic"
midKLen = input.int(14, "%K Length", minval=1, group=midGR)
midKSmooth = input.int(3, "%K Smoothing", minval=1, group=midGR)
midDSmooth = input.int(3, "%D Smoothing", minval=1, group=midGR)
midStochTF = input.string("Chart", "Stochastic Timeframe", options=["Chart", "5 Minutes", "15 Minutes", "1 Hour", "4 Hours", "1 Day", "1 Week", "1 Month"], group=midGR)
midWait = input.bool(true, "Wait for Timeframe Close", group=midGR)
midKColor = input.color(color.aqua, "%K Color", group=midGR)
midDColor = input.color(color.orange, "%D Color", group=midGR)

// ─── Bottom Stochastic ───
botGR = "Bottom Stochastic"
botKLen = input.int(14, "%K Length", minval=1, group=botGR)
botKSmooth = input.int(3, "%K Smoothing", minval=1, group=botGR)
botDSmooth = input.int(3, "%D Smoothing", minval=1, group=botGR)
botStochTF = input.string("Chart", "Stochastic Timeframe", options=["Chart", "5 Minutes", "15 Minutes", "1 Hour", "4 Hours", "1 Day", "1 Week", "1 Month"], group=botGR)
botWait = input.bool(true, "Wait for Timeframe Close", group=botGR)
botKColor = input.color(color.aqua, "%K Color", group=botGR)
botDColor = input.color(color.orange, "%D Color", group=botGR)

// ── Timeframe helper
resolveTF(string choice) =>
    float chartMinutes = timeframe.in_seconds() / 60.0
    switch choice
        "5 Minutes"  => chartMinutes > 5 ? timeframe.period : "5"
        "15 Minutes" => chartMinutes > 15 ? timeframe.period : "15"
        "1 Hour"     => chartMinutes > 60 ? timeframe.period : "60"
        "4 Hours"    => chartMinutes > 240 ? timeframe.period : "240"
        "1 Day"      => timeframe.isintraday ? "D" : timeframe.period
        "1 Week"     => timeframe.isintraday or timeframe.isdaily ? "W" : timeframe.period
        "1 Month"    => timeframe.isintraday or timeframe.isdaily or timeframe.isweekly ? "M" : timeframe.period
        => timeframe.period

// ── Collect candles and independent Stochastic values
collectMiniData(string stTF, int kLen, int kSmooth, int dSmooth, bool waitClose, int maxBars) =>
    var array<float> opens = array.new_float()
    var array<float> highs = array.new_float()
    var array<float> lows = array.new_float()
    var array<float> closes = array.new_float()
    var array<float> kValues = array.new_float()
    var array<float> dValues = array.new_float()

    
    [kHTF, dHTF] = request.security(
         syminfo.tickerid,
         stTF,
         [
             ta.sma(ta.stoch(close, high, low, kLen), kSmooth)[waitClose ? 1 : 0],
             ta.sma(ta.sma(ta.stoch(close, high, low, kLen), kSmooth), dSmooth)[waitClose ? 1 : 0]
         ],
         gaps=barmerge.gaps_off,
         lookahead=barmerge.lookahead_on)

    opens.unshift(open)
    highs.unshift(high)
    lows.unshift(low)
    closes.unshift(close)
    kValues.unshift(kHTF)
    dValues.unshift(dHTF)

    if opens.size() > maxBars
        opens.pop()
        highs.pop()
        lows.pop()
        closes.pop()
        kValues.pop()
        dValues.pop()

    [opens, highs, lows, closes, kValues, dValues]

// ── Draw mini candles, Stochastic lines, levels and values
drawMini(bool enabled, int slot, array<float> os, array<float> hs, array<float> ls, array<float> cs, array<float> ks, array<float> ds, color kCol, color dCol) =>
    var array<line> candleLines = array.new_line()
    var array<line> levelLines = array.new_line()
    var polyline kLine = na
    var polyline dLine = na
    var label kLabel = na
    var label dLabel = na
    var label tfLabel = na

    if barstate.islast
        if candleLines.size() > 0
            for j = 0 to candleLines.size() - 1
                line.delete(candleLines.get(j))
            candleLines.clear()

        if levelLines.size() > 0
            for j = 0 to levelLines.size() - 1
                line.delete(levelLines.get(j))
            levelLines.clear()

        if not na(kLine)
            polyline.delete(kLine)
            kLine := na
        if not na(dLine)
            polyline.delete(dLine)
            dLine := na
        if not na(kLabel)
            label.delete(kLabel)
            kLabel := na
        if not na(dLabel)
            label.delete(dLabel)
            dLabel := na

        if not na(tfLabel)
            label.delete(tfLabel)
            tfLabel := na

        if enabled and os.size() > 1
            int n = math.min(barsToShow, os.size())
            float chartLow = array.slice(ls, 0, n).min()
            float chartHigh = array.slice(hs, 0, n).max()
            float priceRange = math.max(chartHigh - chartLow, syminfo.mintick)
            float baseY = slot == 2 ? topPosition * verticalSpacing : slot == 1 ? midPosition * verticalSpacing : botPosition
            float paneHeight = 0.86

            array<chart.point> kPoints = array.new<chart.point>()
            array<chart.point> dPoints = array.new<chart.point>()

            int firstX = bar_index + xOffset
            int lastX = firstX + n - 1

            // Stochastic Timeframe Label
            string stochTFChoice = slot == 2 ? topStochTF : slot == 1 ? midStochTF : botStochTF
            string stochTFText = switch stochTFChoice
                "Chart"      => timeframe.period
                "5 Minutes"  => "5M"
                "15 Minutes" => "15M"
                "1 Hour"     => "1H"
                "4 Hours"    => "4H"
                "1 Day"      => "1D"
                "1 Week"     => "1W"
                "1 Month"    => "1M"
                => stochTFChoice

            // Stochastic levels: 80 Red, 50 Yellow, 20 Green
            for level in array.from(80.0, 50.0, 20.0)
                float levelY = baseY + paneHeight * level / 100.0
                color levelColor = level == 80.0 ? color.red : level == 50.0 ? color.yellow : color.green
                levelLines.push(line.new(firstX, levelY, lastX, levelY, xloc=xloc.bar_index, color=levelColor, style=line.style_solid, width=1))

            for i = 0 to n - 1
                int idx = n - 1 - i
                int x = firstX + i
                float o = os.get(idx)
                float h = hs.get(idx)
                float l = ls.get(idx)
                float c = cs.get(idx)
                color candleColor = c >= o ? color.teal : color.red

                float yOpen = baseY + paneHeight * (o - chartLow) / priceRange
                float yHigh = baseY + paneHeight * (h - chartLow) / priceRange
                float yLow = baseY + paneHeight * (l - chartLow) / priceRange
                float yClose = baseY + paneHeight * (c - chartLow) / priceRange

                if showCandles
                    candleLines.push(line.new(x, yHigh, x, yLow, xloc=xloc.bar_index, color=candleColor, width=1))
                    candleLines.push(line.new(x, yOpen, x, yClose, xloc=xloc.bar_index, color=candleColor, width=3))
                

                float k = ks.get(idx)
                float d = ds.get(idx)

                if not na(k)
                    kPoints.push(chart.point.from_index(x, baseY + paneHeight * k / 100.0))
                if not na(d)
                    dPoints.push(chart.point.from_index(x, baseY + paneHeight * d / 100.0))

            if kPoints.size() > 1
                kLine := polyline.new(kPoints, false, false, xloc.bar_index, kCol, color(na), line.style_solid, 1)
            if dPoints.size() > 1
                dLine := polyline.new(dPoints, false, false, xloc.bar_index, dCol, color(na), line.style_solid, 1)

                // Show K/D values below each mini chart
                float latestK = ks.get(0)
                float latestD = ds.get(0)
                  
                string stochTFText = slot == 2 ? topStochTF : slot == 1 ? midStochTF : botStochTF
    
                if not na(latestK) and not na(latestD)
                    float valueY = baseY - 0.10
                    bool kIsHigher = latestK >= latestD

                    string firstText = kIsHigher ? "K " + str.tostring(latestK, "#.0") : "D " + str.tostring(latestD, "#.0")
                    string secondText = kIsHigher ? "D " + str.tostring(latestD, "#.0") : "K " + str.tostring(latestK, "#.0")
                    color firstColor = kIsHigher ? kCol : dCol
                    color secondColor = kIsHigher ? dCol : kCol

                    kLabel := label.new(firstX, valueY, firstText, xloc=xloc.bar_index, style=label.style_none, textcolor=firstColor, size=size.normal)
                    dLabel := label.new(firstX + 9, valueY, secondText, xloc=xloc.bar_index, style=label.style_none, textcolor=secondColor, size=size.normal)
                    
                    tfLabel := label.new(firstX + 22, valueY, stochTFText, xloc=xloc.bar_index, style=label.style_none, textcolor=color.white, size=size.normal)

// ── Requests: same chart symbol, independent timeframes
topCandleTF = resolveTF(topChartTF)
midCandleTF = resolveTF(midChartTF)
botCandleTF = resolveTF(botChartTF)

topStTF = resolveTF(topStochTF)
midStTF = resolveTF(midStochTF)
botStTF = resolveTF(botStochTF)

[topO, topH, topL, topC, topK, topD] = request.security(syminfo.tickerid, topCandleTF, collectMiniData(topStTF, topKLen, topKSmooth, topDSmooth, topWait, barsToShow), calc_bars_count=barsToShow + 10)
[midO, midH, midL, midC, midK, midD] = request.security(syminfo.tickerid, midCandleTF, collectMiniData(midStTF, midKLen, midKSmooth, midDSmooth, midWait, barsToShow), calc_bars_count=barsToShow + 10)
[botO, botH, botL, botC, botK, botD] = request.security(syminfo.tickerid, botCandleTF, collectMiniData(botStTF, botKLen, botKSmooth, botDSmooth, botWait, barsToShow), calc_bars_count=barsToShow + 10)

// ── Top / Middle / Bottom
drawMini(showTop, 2, topO, topH, topL, topC, topK, topD, topKColor, topDColor)
drawMini(showMiddle, 1, midO, midH, midL, midC, midK, midD, midKColor, midDColor)
drawMini(showBottom, 0, botO, botH, botL, botC, botK, botD, botKColor, botDColor)
