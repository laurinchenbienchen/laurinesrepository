# import pylint

def vokale_zaehlen(text):
    text = text.lower()
    vokale = 'aeiou'
    count_v = 0
    for i in text:
        if i in vokale:
            count_v += 1
    return count_v


#anzahl_v = vokale_zaehlen('hallo')
#print(anzahl_v)
