from klase.funkcije import *
from klase.ONK import ONK
from klase.Bootstrapping import Bootstrapping


class PSU:
    '''Klasa za ocenjivanje sredine i totala populacije Prostim Slucajnim Uzorkom:
    - količničko ocenjivanje,
    - regresiono ocenjivanje (koristeći ONK model).
    
    Parametri
    ----------
    df : pd.DataFrame
        Kompletnan skup podataka (populacija).
    X : pd.DataFrame
        Matrica objašnjavajućih promenljivih za celu populaciju.
    Y : pd.Series
        Zavisna promenljiva za celu populaciju.
    n : int
        Veličina slučajnog uzorka.
    kategorije : list[str], opciono
        Kategorijske promenljive za kreiranje dummy promenljivih.
    alfa : float ili list, opciono
        Nivo značajnosti za statističko testiranje parametara.
    seed : int, opciono
        Seed za reprodukciju slučajnog uzorka.
    
    Atributi
    ----------
    df : pd.DataFrame
        Kompletan skup podataka.
    uzorak : pd.DataFrame
        Nasumično izabrani prost slučajan uzorak podataka.
    X, x : pd.DataFrame
        Matrice objašnjavajućih promenljivih za populaciju i uzorak.
    Y, y : pd.Series
        Zavisne promenljive za populaciju i uzorak.
    Ym, ym : float
        Srednje vrednosti zavisne promenljive u populaciji i uzorku.'''
    def __init__(self, df, X, Y, n, kategorije = None, alfa= [0.1, 0.05, 0.01], seed=42):
        self.df = df.copy()
        self.n = n
        self.N = len(df)
        self.f = n / self.N
        self.seed = seed
        self.alfa = alfa
        self.uzorak = df.sample(n=n, replace=False, random_state=seed)

        self.model = ONK(alfa)
        if kategorije is not None:
            self.X = self.model.vestacke(kategorije= kategorije, x = X)
            self.x = self.model.vestacke(kategorije= kategorije, x = X.loc[list(self.uzorak.index)])
        else:
            self.X = X
            self.x = X.loc[self.uzorak.index]
        
        self.Y = self.df['plata']
        self.y = self.uzorak['plata']
        self.Ym = self.Y.mean()
        self.Xm = self.X.mean()
        self.ym = self.y.mean()
        self.xm = self.x.mean()

        self.bs = None

    @property
    def describe(self):
        ''' Prikazuje opisne statistike za populaciju i uzorak, uključujući totale mesečnih zarada i godina obrazovanja.'''
        print('--- OPIS PODATAKA ---\n')
    
        print('Uzorak:')
        display(self.uzorak.describe())
    
        print('\nPopulacija:')
        display(self.df.describe())
    
        rezultati = pd.DataFrame({
            'Total mesečne zarade': [form(self.Y.sum()), form(self.y.sum() / self.f)],
            'Total godina obrazovanja': [form(self.X['obrazovanje'].sum()), form(self.x['obrazovanje'].sum() / self.f)]
        }, index=['Populacija', 'Uzorak (korigovan)'])
    
        print('\n--- TOTALI OBELEŽJA ---\n')
        display(rezultati)

    
    def kolicnickoOcenjivanje(self, var='obrazovanje'):
        '''Količničko ocenjivanje sredine i totala Y, 
        sa pristrasnošću i intervalima poverenja.

        Parametri:
        ----------
        var : str
            Promenljiva za količničko ocenjivanje.'''
        x = self.x[var]
        X = self.X[var]

        R = self.Y.sum() / X.sum()
        Ru = self.y.sum() / x.sum()

        YbarKapa = Ru * X.mean()
        YtotalKapa = Ru * X.sum()
        pristrastnostR = YbarKapa - self.Y.mean()
        rel_pristrastnost = (pristrastnostR / self.Y.mean()) * 100
        pristrasnostTotal = YtotalKapa - self.Y.sum()

        rezultati = pd.DataFrame({'Vrednost': [form(R), form(Ru), form(YbarKapa), form(self.Y.mean()), form(pristrastnostR),
                                               f'{rel_pristrastnost:.2f}%', form(YtotalKapa), form(self.Y.sum()), form(pristrasnostTotal)]},
                                 index=['Količnik populacije (R)', 'Količnik uzorka (Ru)', 'Sredina Y količnički', 'Stvarna sredina Y',
                                        'Pristrasnost sredine', 'Relativna pristrasnost (%)', 'Total Y količnički', 'Stvarni total Y', 'Pristrasnost totala'])

        print('\n--- KOLIČNIČKO OCENJIVANJE ---\n')
        display(rezultati)

        s = np.square(self.Y - X * R).sum()
        SYt = np.sqrt(s * (self.N**2 * (1 - self.f)) / (self.n * (self.N - 1)))
        SYm = np.sqrt(s * (1 - self.f) / (self.n * (self.N - 1)))
        SR = np.sqrt(s * (1 - self.f) / (self.n * X.mean()**2 * (self.N - 1)))

        devijacije = pd.DataFrame({
            'Standardna devijacija': [form(SYt), form(SYm), form(SR)]
        }, index=['Totala Y', 'Sredine Y', 'Količnika'])

        print('\n--- STANDARDNE DEVIJACIJE ---')
        display(devijacije)

        self.intervaliPoverenja(YbarKapa, SYm)

        self.SKGR = pristrastnostR**2 + SYm**2

    def regresionoOcenjivanje(self, alfa=0.1):
        ''' Regresiono ocenjivanje sredine i totala korišćenjem ONK modela.
    
        Parametri:
        ----------
        alfa : float
            Nivo značajnosti za eliminaciju promenljivih. '''
        print('\n--- REGRESIONO OCENJIVANJE ---')
    
        self.model.fit(self.X, self.Y)
        self.X = self.model.x
        rezultat = self.model.fit(self.x, self.y)
    
        print('\nMetodom običnih najmanjih kvadrata ocenjen je model:')
        display(rezultat)
    
        print('\nZnačajni parametri nakon iterativne eliminacije:')
        znacajni_rezultat = self.model.fitsig(alfa)
        display(znacajni_rezultat)
        self.x = self.model.x
        self.X = self.X.loc[:, list(self.x.columns)]
    
        print('\nJednačina modela:')
        print(self.model.matOblik)
    
        xm = self.x.mean()
        Xm = self.X.mean()
    
        ybarlr = self.ym + (Xm - xm) @ self.model.b
        pristrasnostLr = ybarlr - self.Ym
    
        rho = self.x.loc[:, self.x.std() > 0].apply(lambda col: col.corr(self.y))
        sy = sum(np.square(self.y - self.Ym)) / (self.n - 1)
        Sylrs = np.sqrt((1 - rho**2) * sy * ((1 - self.f) / self.n))
    
        ybarlr2 = self.model.predict(self.x, mean=True)
    
        rezultati_sredina = pd.DataFrame({
            'Vrednost': [
                form(ybarlr),
                form(Sylrs.mean()),
                form(pristrasnostLr),
                form(ybarlr2)
            ]
        }, index=[
            'Regresiona ocena sredine (poznat Xm)',
            'Standardna devijacija regresione ocene',
            'Pristrasnost regresione ocene',
            'Regresiona ocena sredine (uzorak)'
        ])
    
        print('\n--- OCENE SREDINE ---')
        display(rezultati_sredina)
    
        self.intervaliPoverenja(ybarlr, Sylrs.mean())
    
        Ytotallr1 = self.model.predict(self.X, total=True)
        Ytotallr2 = self.model.predict(self.x, total=True) * self.N / self.n
    
        rezultati_total = pd.DataFrame({
            'Vrednost': [form(Ytotallr1), form(Ytotallr2), form(self.Y.sum())]
        }, index=[
            'Regresiona ocena totala (populacija)',
            'Regresiona ocena totala (proširen uzorak)',
            'Stvarni total'
        ])
    
        print('\n--- OCENE TOTALA ---')
        display(rezultati_total)
    
        self.SKGLr = pristrasnostLr**2 + Sylrs.mean()**2
    
        rezultati_skg = pd.DataFrame({
            'Vrednost': [form(self.SKGR), form(self.SKGLr)]
        }, index=[
            'SKG količničkog ocenjivanja',
            'SKG regresionog ocenjivanja'
        ])
    
        print('\n--- SREDNJE KVADRATNE GREŠKE ---')
        display(rezultati_skg)

    def intervaliPoverenja(self, ocena, stdev, parametar = None):
        ''' Formira DataFrame sa intervalima poverenja za datu ocenu.
    
        Parametri:
        ----------
        ocena : float
            Procena sredine ili totala.
        stderr : float
            Standardna greška procene.
        parametar : float, opciono
            Prava vrednost za proveru da li se nalazi u intervalu.'''
        parametar = self.Ym if parametar is None else parametar
        intervali = []
        for a in self.alfa:
            t = stats.t.ppf(1 - a / 2, self.n - 1)
            donja = ocena - t * stdev
            gornja = ocena + t * stdev
            raspon = gornja - donja
            if parametar is not None:
                sadrzi = 'DA' if donja <= parametar <= gornja else 'NE'
                intervali.append([ocena, stdev, f'{(1 - a)*100:.1f}%', form(donja), form(gornja), form(raspon), sadrzi])
            else:
                intervali.append([ocena,stdev, f'{(1 - a)*100:.1f}%', form(donja), form(gornja), form(raspon)])

        kolone = ['Ocena', 'Standardna devijacija','Interval', 'Donja granica', 'Gornja granica', 'Raspon']
        if parametar is not None:
            kolone.append('Sadrži pravu vrednost')
    
        df_intervali = pd.DataFrame(intervali, columns=kolone).set_index('Interval')
        print(f'\n--- INTERVALI POVERENJA ---')
        display(df_intervali)
        return df_intervali

    def plot(self, k=1000):
        ''' Vizualizuje distribuciju Bootstrapping proseka plata iz uzorka,
        koristeći plotDist iz klase Bootstrapping.
        
        Parametri:
        ----------
        k : int
            Broj Bootstrapping uzoraka. Podrazumevano: 1000'''
        if self.bs is None:
            self.bs = Bootstrapping(self.df, alfa=self.alfa, n=self.n)
            self.bs.fit(k)
        self.bs.plotDist(alfa= self.alfa, target = self.y.mean())
    def minimalni_interval(self, k = None):
        ''' Određuje najveći nivo značajnosti (najmanji interval poverenja) u kojem
        se prosečna vrednost ciljne promenljive iz uzorka nalazi unutar 
        bootstrap distribucije srednjih vrednosti.''' 
        target_mean = self.y.mean()
        alfe = np.linspace(0.001, 1, 500)[::-1]
        k = 3000 if k is None else k
        if self.bs is None:
            self.bs = Bootstrapping(self.df, alfa=self.alfa, n=self.n)
            self.bs.fit(k)
        for a in alfe:
            
            interval = self.bs.interval(alfa=a).iloc[0]
            donja, gornja = interval['donja'], interval['gornja']
            if donja <= target_mean <= gornja:
                if a not in self.alfa:
                    self.alfa.append(a)
                    self.alfa = sorted(self.alfa)
                return 1 - a
            
        return None

    def __repr__(self):
        return f"{form(self.ym)}"


class SSU(PSU):
    ''' Stratifikovani Slučajni Uzorak (SSU) - podklasa PSU klase,
    koristi se za ocenjivanje sredine i totala populacije sa stratifikacijom.
    
    Omogućava količničko i regresiono ocenjivanje unutar stratumskih podela,
    uz posebne i kombinovane procene, kao i proračun varijanse po stratumima.'''
    def __init__(self, df, X, Y, n, stratumi, alfa=[0.1, 0.05, 0.01], seed=1304):
        ''' df : pd.DataFrame
            Populacija (kompletan skup podataka).
        X : pd.DataFrame
            Matrica nezavisnih promenljivih.
        Y : pd.Series
            Zavisna promenljiva (npr. 'plata').
        n : int
            Veličina ukupnog uzorka.
        stratumi : list[str]
            Kolone koje definišu stratume.
        alfa : list[float], opciono
            Nivoi značajnosti. Podrazumevani: [0.1, 0.05, 0.01].
        seed : int, opciono
            Seed za reproduktivnost izbora uzorka.'''
        super().__init__(df, X, Y, n, alfa=alfa, seed=seed)

        self.df['Strata'] = self.df[stratumi].astype(str).agg('_'.join, axis=1)
        self.stratumi = stratumi
        self.strataCounts = self.df['Strata'].value_counts(normalize=True)
        self.nh = (self.strataCounts * n).round().astype(int)
    
        self.uzorak = pd.concat([self.df[self.df['Strata'] == strata].sample(n=size, random_state=seed) 
                                 for strata, size in self.nh.items()])
        self.x = self.uzorak['obrazovanje']
        self.y = self.uzorak['plata']
        self.X = self.df['obrazovanje']
        self.Xtotal = self.X.sum()
        self.Y = self.df['plata']
        self.Ym = self.Y.mean()
        self.Ytotal = self.Y.sum() 
        self.N = self.df.shape[0]
        self.n = self.uzorak.shape[0]
        self.f = self.n / self.N
        self.nh = self.uzorak['Strata'].value_counts()
        self.Nh = self.df['Strata'].value_counts()
        self.ybarh = self.uzorak.groupby('Strata')['plata'].mean()
        self.Wh = self.Nh / self.N
        self.fh = self.nh / self.Nh
        self.S2h = self.uzorak.groupby('Strata')['plata'].var()
        
    def describe(self):
        '''Prikazuje deskriptivnu statistiku uzorka i populacije, po stratumima.
    Takođe računa i prikazuje ocene sredine i totala uz intervale poverenja.'''
        print("--- Uzorak: ---")
        display(pd.DataFrame(self.nh))
        display(self.uzorak.describe())
        print("--- Populacija: ---")
        display(self.df.describe())
        self.ybarSt = self.Nh @ self.ybarh / self.N

        VybarSt = ((1 - self.f) / self.N) * self.Wh @ (self.S2h)
        SybarSt = np.sqrt(VybarSt)
        intervali = []
        self.intervaliPoverenja(self.ybarSt, SybarSt)

        YtotalSt = self.N * self.ybarSt
        SYtotalSt = self.N * SybarSt

        self.intervaliPoverenja(YtotalSt, SYtotalSt, parametar= self.Y.sum())
        
    def kolicnickoOcenjivanje(self):
        ''' Sprovodi posebnu i kombinovanu količničku ocenu sredine i totala
    koristeći podatke po stratumima. Računa korelacije i varijanse.

    Prikazuje rezultate sa pristrasnošću, intervalima poverenja
    i srednjim kvadratnim greškama (SKG).'''
        Yh = self.df.groupby('Strata')['plata'].sum()
        Xh = self.df.groupby('Strata')['obrazovanje'].sum()
        Rh = Yh / Xh
        self.rho = self.uzorak.groupby('Strata')['obrazovanje'].corr(self.y)
        yh = self.uzorak.groupby('Strata')['plata'].sum()
        xh = self.uzorak.groupby('Strata')['obrazovanje'].sum()
        Sx2h = self.uzorak.groupby('Strata')['obrazovanje'].var()
        YtotalRs = (yh / xh) @ (Xh)
        SYtotalRs = np.sqrt((((np.square(self.Nh) * (1 - self.f))) / self.nh) @ 
                            ((self.S2h + np.square(Rh) * Sx2h - (2 * Rh * self.rho.values * np.sqrt(self.S2h) * np.sqrt(Sx2h)))))

        YbarRs = YtotalRs / self.N
        SYbarRs = SYtotalRs / self.N
        
        print('\n--- POSEBNA KOLIČNIČKA OCENA ---\n')

        print('korelacija godina obrazovanja sa zaradom po stratumima'.upper())
        display(pd.DataFrame(self.rho))

        self.intervaliPoverenja(YbarRs, SYbarRs, parametar= self.Ym)
        self.intervaliPoverenja(YtotalRs, SYtotalRs, parametar= self.Ytotal)


        print('\n--- KOMBINOVANA KOLIČNIČKA OCENA ---\n')
        xbarh = self.uzorak.groupby('Strata')['obrazovanje'].mean()
        xbarSt = self.Nh.dot(xbarh) / self.N
        YtotalRc = self.ybarSt / xbarSt * self.Xtotal
        YbarRc = YtotalRc / self.N

        display(pd.DataFrame({'Ocena': [YbarRc, YtotalRc], 'Stvarna vrednost': [self.Ym, self.Ytotal],
                              'Pristrasnost': [YbarRc - self.Ym, YtotalRc - self.Ytotal]} ,
                             index=['Sredina', 'Total']))
        self.SKGRs = np.square(YbarRs - self.Ym) + np.square(SYbarRs)


    def regresionoOcenjivanje(self):
        '''Regresiono ocenjivanje po stratumima: za svaki stratum posebno se trenira ONK model.

        alfa : float
            Nivo značajnosti
        
        Prikazuje ocene sredina po stratumima, njihovu pristrasnost i
        formira intervale poverenja za ukupnu regresionu procenu.
        Računa SKG regresione metode.'''
        x = self.uzorak[['obrazovanje', 'Strata']]
        y = self.uzorak[['plata', 'Strata']]
        X = self.df[['obrazovanje', 'Strata']]
        Y = self.df[['plata', 'Strata']]
        b = pd.DataFrame()
        for ime, grupa in self.uzorak.groupby('Strata'):
            y = grupa['plata']
            x = grupa[['obrazovanje']]
            model = ONK()
            model.fit(x, y)
            b[ime] = model.b
        b = b.T
        print('\n--- REGRESIONI KOEFICIENTI PO STRATUMIMA ---\n')
        display(b)

        Xbarh = self.df.groupby('Strata')['obrazovanje'].mean()
        xbarh = self.uzorak.groupby('Strata')['obrazovanje'].mean()
        ybarlrh = self.ybarh + b.loc[:, 'obrazovanje'] * (Xbarh - xbarh)
        ybarlrh.name = 'Ocena'
        self.ybarh.name = 'Stvarna vrednost'
        print('\n--- REGRESIONA OCENA PO STRATUMIMA ---\n')
        display(pd.DataFrame({'Ocena': ybarlrh.values, 'Stvarna vrednost': self.ybarh.values, 'Pristrasnost': ybarlrh.values - self.ybarh.values},
                             index = ybarlrh.index))

        ybarlrs = self.Wh.dot(ybarlrh)
        Sybarlrs = np.sqrt(((np.square(self.Wh) * (1 - self.fh)) / self.nh).dot(self.S2h * (1 - np.square(self.rho))))
        self.intervaliPoverenja(ybarlrs, Sybarlrs, parametar= self.Ym)

        SKGLr = np.square(ybarlrs - self.Ym) + np.square(Sybarlrs)    
        display(pd.DataFrame({'Vrednost': [form(self.SKGRs), form(SKGLr)]}, 
                                     index=['SKG količničkog ocenjivanja','SKG regresionog ocenjivanja']))
