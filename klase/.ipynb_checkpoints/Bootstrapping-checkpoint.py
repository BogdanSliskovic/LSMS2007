from klase.funkcije import *

class Bootstrapping():
    ''' Klasa za primenu metode uzorkovanja sa vraćanjem na DataFrame-u radi procene srednje vrednosti, standardne devijacije,
    intervala poverenja, kao i određivanja potrebne veličine uzorka.'''
    def __init__(self, df, alfa = None, n=None):
        '''df : pandas.DataFrame
        alfa : float ili lista float-ova, opciono
            Nivo/i značajnosti za određivanje intervala poverenja.
            Podrazumevane vrednosti su [0.1, 0.05, 0.01].
        
            Ako je unet float/int, vrednost mora biti između 0 i 1.
            Ako je uneta lista, sve vrednosti moraju biti između 0 i 1.
        
        n : int, opciono
            Veličina uzorka za bootstrap. Ukoliko nije navedeno, koristi se 10% od ukupne veličine DataFrame-a.'''
        self.df = df
        default = [0.1, 0.05, 0.01]
        if alfa is None:
            self.alfa = default
        elif isinstance(alfa, (float, int)):
            if alfa < 0 or alfa > 1:
                raise ValueError('Alfa mora biti izmedju 1 i 0')
            self.alfa = sorted(set(default + [alfa]))
        else:
            for a in alfa:
                if a < 0 or a > 1:
                    raise ValueError('Alfa mora biti izmedju 1 i 0')
            self.alfa = sorted(set(default + list(alfa)))
        self.n = n if n is not None else int(len(df) * 0.1)
    
        self.N = len(df)

    def fit(self, k, seed=42):
        ''' Kreira k uzoraka sa vraćanjem i računa njihove srednje vrednosti i standardne devijacije'''
        self.sredineUzoraka = []
        self.standardneDevijacije = []
        for i in range(k):
            uzorak = self.df['plata'].sample(n=self.n, random_state=seed + i)
            self.sredineUzoraka.append(uzorak.mean())
            self.standardneDevijacije.append(uzorak.std())
        self.sredineUzoraka = pd.Series(self.sredineUzoraka, name = 'prosek')
        self.standardneDevijacije = pd.Series(self.standardneDevijacije, name = 'standardna devijacija')

    @property
    def sredina(self):
        ''' Prosečna vrednost srednjih vrednosti bootstrap uzoraka'''
        return self.sredineUzoraka.mean()

    @property
    def std(self):
        ''' Prosečna vrednost standardnih devijacija bootstrap uzoraka'''
        return self.standardneDevijacije.mean()

    def interval(self, alfa = None, x = None):
        '''Računa intervale poverenja za srednje vrednosti uzoraka
        za zadate nivoe značajnosti'''
        x = self.sredineUzoraka if x is None else x
        alfa = self.alfa if alfa is None else alfa
        alfa = np.atleast_1d(alfa)
        intervali = []
        for a in alfa:
            
            donja = x.quantile(a / 2)
            gornja = x.quantile(1 - a / 2)
            intervali.append([donja, gornja])
        return pd.DataFrame(intervali, columns=["donja", "gornja"], index = [f"{int((1 - a) * 100)}%" for a in alfa])

    def d(self, alfa = None):
        ''' Polovina širine intervala poverenja za zadati nivo značajnosti alfa.'''
        alfa = self.alfa if alfa is None else alfa
        intervals = self.interval(alfa)
        return ((intervals["gornja"] - intervals["donja"]) / 2).rename('d')

    def plotDist(self, alfa = None, x = None, target = None):
        ''' Vizuelizuje distribuciju srednjih vrednosti iz realizovanih uzoraka
        sa intervalima poverenja i opcionim ciljnim prosekom (koristi se u klasi PSU i SSU)'''
        x = self.sredineUzoraka if x is None else x
        alfa = self.alfa if alfa is None else alfa
        boje = plt.cm.tab10.colors
        plt.figure(figsize=(12, 6))
        sns.histplot(x, bins=50, kde=True, color='skyblue', edgecolor='black', stat="count")
        plt.title(f'Distribucija bootstrap {x.name} plata', fontsize=16)
        plt.xlabel(f'{x.name} plata', fontsize=14)
        plt.ylabel('Frekvencija', fontsize=14)
        plt.grid(True)

        plt.axvline(x=x.mean(), color='blue', linestyle='-', label=f'Srednja vrednost: {x.mean():.2f}')
        for a, boja in zip(alfa, boje):
            donja, gornja =  self.interval(a, x = x).iloc[0]
            plt.axvline(x=donja, color= boja, linestyle='--', label=f'{int((1 - a)*100)}% interval')
            plt.axvline(x=gornja, color= boja, linestyle='--')
            
        if target is not None:
            plt.axvline(target.mean(), color='red', linestyle='-', linewidth=2, label=f'Target: {target.mean():.2f}')

        plt.legend()
        plt.show()

    def obimUzorka(self, alfa = None):
        ''' Računa optimalni obim uzorka za svaki nivo značajnosti'''
        alfa = self.alfa if alfa is None else alfa
        alfa = np.atleast_1d(alfa)
        nList, dList, indeksi = [], [], []
    
        for a in alfa:
            d = self.d([a]).values[0]
            Z = stats.norm.ppf(1 - a / 2)
            Sy2 = np.square(self.standardneDevijacije).mean()
            n0 = (np.square(Z) * Sy2) / np.square(d)
            n = int(1 / (1 / n0 + 1 / self.N))
            nList.append(n)
            indeksi.append(f"{int((1 - a) * 100)}%")
            dList.append(d)
    
        return pd.DataFrame({'n': nList, 'd': dList}, index=indeksi)

    @property
    def summary(self):
        '''Prikaz svih ključnih statistika i Jarque-Bera testa'''
        data = pd.Series({"Prosečna sredina": self.sredina, "Prosečna standardna devijacija": self.std})
        
        d = self.d()
        d.index = [f"d({(1 - a) * 100:.0f})%" for a in self.alfa]
    
        data = pd.concat([data,jb(self.sredineUzoraka)])
    
        return pd.DataFrame(data)
        
    def __repr__(self):
        return f"Bootstrap | n={self.n} | N={self.N} | bootstrap uzoraka={len(self.sredineUzoraka)}"
