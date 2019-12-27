from market.marketdata import MktData
from graph.graphdrawer import draw_terminal, draw_to_image

def main():
    md = MktData()
    df = md.get_data_from_csv('../../resources/BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')

    draw_to_image(df['Date'].tolist(), df['24h Low (USD)'].tolist(), 'image.png')
    draw_terminal([x for x in range(0, len(df))], df['24h Low (USD)'].tolist())

main()
