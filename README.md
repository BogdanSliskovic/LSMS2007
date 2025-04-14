# Teorija uzoraka i planiranje eksperimenata – LSMS Srbija 2007

Ovaj projekat je seminarski rad iz predmeta **Teorija uzoraka i planiranje eksperimenata**.  
U radu se koriste podaci iz LSMS ankete u Srbiji iz 2007. godine za ocenjivanje prosečne i ukupne mesečne zarade, primenom različitih metoda uzorkovanja i statističke analize.

---

## 📁 Struktura projekta

- **`TU.dta`**  
  Sadrži podatke iz LSMS ankete za Srbiju (2007).  
  Zadržane su samo relevantne varijable i zaposleni ispitanici.

- **`TUPA.ipynb`**  
  Glavni Jupyter notebook sa detaljno iskomentarisanim analizama i primenom svih metoda.  
  Kroz ovaj fajl se vodi ceo tok seminara – od učitavanja podataka do zaključaka.

- **`/klase/`**  
  Folder koji sadrži sve Python klase korišćene u notebooku `TUPA.ipynb`.  
  Klasni modeli su razdvojeni radi preglednosti i modularnosti:
  
  | Fajl             | Sadržaj |
  |------------------|---------|
  | `Bootstrapping.py` | Klasa za uzorkovanjem sa ponavljanjem |
  | `ONK.py`          | Linearni regresioni model koji se trenira metodom Običnih Najmanjih Kvadrata |
  | `Sampling.py`     | Klase za Prosti i Stratifikovani slučajni uzorak |
  | `funkcije.py`     | Zajedničke funkcije: `jb()`, `form()`|

