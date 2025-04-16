# Teorija uzoraka i planiranje eksperimenata – LSMS Srbija 2007

U ovom radu korišćeni su podaci iz ankete Living Standards Measurement Study (LSMS), koju je u ime Svetske banke sproveo Republički zavod za statistiku u maju i junu 2007. godine na teritoriji Republike Srbije. Ova anketa pruža detaljne informacije o životnim uslovima, ekonomskim aktivnostima i demografskim karakteristikama stanovnika Srbije, a njen cilj je da pomogne u boljem razumevanju faktora koji utiču na socijalni i ekonomski status građana. Podaci iz LSMS-a omogućavaju analizu različitih aspekata života, a u ovom radu fokusiraću se na analizu mesečnih zarada, kako bih utvrdio koji faktori utiču na njihove varijacije u Srbiji i u kojoj meri svaki od njih doprinosi tim razlikama. Prosečna mesečna zarada korišćena je kao pokazatelj ekonomske situacije, pružajući uvid u životne uslove prosečnog stanovnika zemlje. Takođe, ukupne godišnje zarade predstavljaju značajan pokazatelj ekonomske situacije, jer direktno utiču na bruto domaći proizvod zemlje.

Anketna pitanja za odabrane varijable:

	-plata: Neto prihod prethodnog meseca od glavnog posla

	-obrazovanje: U upitniku je ispitanicima data ISCED skala, varijabla prekodirana tako da predstavlja godine obrazovanja

	-obr3: Tri obrazovne kategorije (osnovna, srednja, visoka škola)

	-starost: Godine ispitanika u trenutku anketiranja

	-satiRada: Koliko sati je ispitanik radio na glavnom poslu u toku prethodne nedelje

	-zene: dve kategorije (Zena, Muskarac)

	-urban: dve kategorije (Grad, Selo)

	-region: četiri kategorije (Beograd, Vojvodina, Zapadna Srbija i Šumadija, Južna i jugoistočna Srbija)


## Struktura projekta

- [TUPE.ipynb](TUPE.ipynb)  
  Glavni Jupyter notebook sa detaljno iskomentarisanim analizama i primenom svih metoda.  
  Kroz ovaj fajl se vodi ceo tok seminara – od učitavanja podataka do zaključaka.

- [TU.dta](TU.dta)   
  Sadrži podatke iz LSMS ankete za Srbiju (2007).  
  Zadržane su samo relevantne varijable i zaposleni ispitanici.

- [klase/](klase/) 
  Folder koji sadrži sve Python klase korišćene u notebooku `TUPA.ipynb`.  
  Klasni modeli su razdvojeni radi preglednosti i modularnosti:
  
  | Fajl             | Sadržaj |
  |------------------|---------|
  | [`Bootstrapping.py`](klase/Bootstrapping.py) | Klasa za uzorkovanjem sa ponavljanjem |
  | [`ONK.py`](klase/ONK.py)          | Linearni regresioni model koji se trenira metodom Običnih Najmanjih Kvadrata |
  | [`Sampling.py`](klase/Sampling.py)     | Klase za Prosti i Stratifikovani slučajni uzorak |
  | [`funkcije.py`](klase/funkcije.py)     | Zajedničke funkcije: `jb()`, `form()`|

