

from dueunits import DUEUnit

due = DUEUnit()

due.setBase("http://www.unit-test.org")

News_Seeds = ["http://www.bbc.co.uk",
              "http://edition.cnn.com",
              "http://www.bloomberg.com",
              "http://www.ted.com/talks/tags",
              "http://www.foxnews.com",
              "http://www.time.com/time",
              "http://www.nationalgeographic.com",
              "http://www.bbcfocusmagazine.com",
              "http://www.pcmag.com",
              "http://www.drdobbs.com",
              "http://news.google.com",
              "http://www.channelnewsasia.com",
              "http://health.usnews.com",
              "http://www.zdnet.co.uk",
              "http://soccernet.espn.go.com",
              "http://mlb.mlb.com",
              "http://www.dallasnews.com",
              "http://www.theaustralian.com.au",
              "http://www.nydailynews.com" ]

due.ust(News_Seeds)

#Seed = "http://www.bbc.co.uk"
#if due.ust(Seed):
#    print True

for seen in due.ust(News_Seeds):
    print seen

due.savetofile()

for seen in due.ust(News_Seeds):
    print seen