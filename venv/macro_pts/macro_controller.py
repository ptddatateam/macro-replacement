import transits
import ferry_macro
import ferry_sw
import cproviders
import cproviders_sw
import statewide_transit_rollup


def main(year_of_report, output_path, prettyFormatting):

    year2 = year_of_report-1
    year1 = year_of_report-2

    mode = input('Please select the mode you would like to output: transits, community providers, ferries, or all?')
    mode = 'transits'
    if mode == 'transits':
        transits.main(year1, year2, year_of_report, output_path, prettyFormatting)
    elif mode == 'community providers':
        cproviders.main(year1, year2, year_of_report, output_path)
        cproviders_sw.main(year1, year2, year_of_report, output_path)
    elif mode == 'ferries':
        ferry_macro.main(year1, year2, year_of_report, output_path)
        ferry_sw.main(year1, year2, year_of_report. output_path)
    elif mode == 'all':
        transits.main(year1, year2, year_of_report, output_path, prettyFormatting)
        cproviders.main(year1, year2, year_of_report, output_path)
        cproviders_sw.main(year1, year2, year_of_report, output_path)
        ferry_macro.main(year1, year2, year_of_report, output_path)
        ferry_sw.main(year1, year2, year_of_report, output_path)
    else:
        print('Try Again!')








if __name__ == "__main__":
    main(2017, r'C:\Users\SchumeN\Documents\ptstest\newtest', True)