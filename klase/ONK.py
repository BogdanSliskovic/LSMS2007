from klase.funkcije import *

class ONK:
    ''' Klasa za regresionu analizu metodom običnih najmanjih kvadrata (ONK).'''
    def __init__ (self, alfa = None):
        '''alfa : float ili list, opciono
        Rizik greške za statističko testiranje koeficijenata.
        Podrazumevano: [0.1, 0.05, 0.01].'''
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
        for attr in ['x', 'y', 'm', 'n', 'b', 'bstd', 'tstat']:
            setattr(self, attr, None)
        

    def fit(self,x ,y, konstanta = True, kategorije = None):
        '''
        Trenira regresioni model metodom običnih najmanjih kvadrata.

        Parametri:
        ----------
        x : pd.DataFrame
            Matrica nezavisnih promenljivih.
        y : pd.Series
            Zavisna promenljiva.
        konstanta : bool, opciono
            Da li uključiti slobodni član.
        kategorije : list[str], opciono
            Lista kategorijskih promenljivih za kreiranje veštačkih varijabli.

        Rezultat:
        ----------
        pd.DataFrame
            Tabela sa koeficijentima, standardnim greškama i t-statistikama.
        '''
        self.x = x.copy()
        self.y = y.copy()
        self.m = self.x.shape[0]
        self.n = self.x.shape[1]
        self.t = {a : abs(stats.t.ppf( a / 2, self.m - self.n)) for a in self.alfa}


        if any(kat in self.x.columns for kat in ['region', 'zene', 'urban', 'obr3']):
            self.vestacke(kategorije)
            self.x = self.x.astype(float)
        
        if konstanta and 'const' not in self.x.columns:
            self.x.insert(0,'const',1)
        
        self.n = self.x.shape[1]

    
        self.b = pd.Series(np.linalg.inv(self.x.T @ self.x) @ (self.x.T @ self.y), index = self.x.columns)
        ykappa = self.x @ self.b
        res = self.y - ykappa
        sigma2 = res.T @ res / (self.m - self.n)
        self.bstd = pd.Series(np.sqrt(np.diag(np.linalg.inv(self.x.T @ self.x) * sigma2)),index = self.x.columns)
        self.tstat = pd.Series(self.b / self.bstd, index = self.x.columns)
   
    
        sig = self.tstat.apply(lambda t:  "*" * sum(abs(t) >= self.t[a] for a in [.1, .05, .01]) if abs(t) > self.t[0.1] else '')
 
        model = pd.concat([self.b,self.bstd,self.tstat, sig],axis = 1)
        model.columns = ['koeficijent', 'std', 't', 'sig']
        return model

    def fitsig(self, alfa = 0.1):
        '''
        Iterativno uklanja statistički nebitne promenljive po zadatom alfa.

        Parametri:
        ----------
        alfa : float
            Nivo značajnosti za eliminaciju promenljivih.

        Rezultat:
        ----------
        pd.DataFrame
            Rezultujući model sa značajnim promenljivima.
        '''
        self.fit(self.x, self.y)
        maska = (~self.b.index.str.contains('region')) & (~self.b.index.str.contains('const'))
        
        for i in range(len(self.b[maska])):
            if abs(self.tstat[maska].iloc[i]) < self.t[alfa]:
                print(f'Promenjiva {self.b[maska].index[i]} je statisticki neznacajna, t vrednost:\n{self.tstat[maska].iloc[i]}')
                self.x = self.x.drop(self.b[maska].index[i], axis = 1)
                self.n = self.x.shape[1]
                maska = (~self.b.index.str.contains('region')) & (~self.b.index.str.contains('const'))
                return self.fitsig(alfa)
        if (abs(self.b[~maska].drop('const') / self.bstd[~maska].drop('const')) < self.t[alfa]).all():
            self.x = self.x.drop(x.columns[x.columns.str.startswith('region')], axis = 1)
            self.n = x.shape[1]
            self.b = self.b[~self.b.index.str.startswith('region')]
            print(f'Regioni su statisticki neznacajni t statistike :\n {self.tstat[~maska].drop('const')}')

        return self.fit(self.x, self.y)
        
    @property
    def matOblik (self):
        ''' Prikazuje regresionu jednačinu u tekstualnom obliku.'''
        koeficijenti = []
        for var,koef in self.b.items():
            if var.lower() == 'const':
                koeficijenti.append(f'{form(koef)}')
            else:
                koeficijenti.append(f'{form(koef)} *{var}')
        jednacina = f"{self.y.name} = " + " + ".join(koeficijenti)
        return jednacina

    def predict(self, x = None, mean = False, total = False):
        '''
        Predviđa vrednosti zavisne promenljive.

        Parametri:
        ----------
        x : pd.DataFrame
            Matrica novih podataka za predikciju.
        mean : bool
            Da li vratiti srednju vrednost predikcija.
        total : bool
            Da li vratiti sumu predikcija.

        Rezultat:
        ----------
        float ili pd.Series
            Predikcije zavisne promenljive.
        '''
        x = self.x if x is None else x
        predikcija = x @ self.b
        if mean:
            return predikcija.mean()
        elif total:
            return predikcija.sum()
        else:
            return predikcija

    def vestacke(self, kategorije , x = None):
        '''Kreira dummy varijable za navedene kategorijske promenljive.

        Parametri:
        ----------
        kategorije : list[str]
            Lista kategorijskih promenljivih za konverziju.
        x : pd.DataFrame, opciono
            DataFrame za kreiranje dummy varijabli.
            Ukoliko nije navedeno, koristi originalne podatke.

        Rezultat:
        ----------
        pd.DataFrame
            DataFrame sa dummy varijablama.'''
        x = self.x if x is None else x.copy()
        if 'const' not in x.columns:
            x.insert(0,'const',1)            
        for kat in kategorije:
            for red in sorted(x[kat].unique())[1:]:
                x[f'{kat}_{red}'] =  (x[kat] == red).astype(float)
            x.drop(kat, axis = 1, inplace = True)
            self.x = x
        return self.x

    @property
    def pregled(self):
        '''Prikazuje tabelu sa ključnim statističkim pokazateljima modela.'''
        ypred = self.predict(self.x)
        res = self.y - ypred
        res.name = 'reziduali'
        self.res = self.y - ypred
        SSR = (res ** 2).sum()
        SSY = ((self.y - self.y.mean()) ** 2).sum()
        R2 = 1 - SSR / SSY
        F = (R2 / self.n) / ((1 - R2) / (self.m - self.n - 1))
        p = 1 - stats.f.cdf(F, dfn=self.n, dfd=self.m - self.n - 1)
        JB = jb(res)
        
        MSE = (res ** 2).mean()
        RMSE = np.sqrt(MSE)
        MAE = res.abs().mean()
    
        data = pd.DataFrame([self.m,  form(R2),form(F),p, JB.iloc[0], JB.iloc[1],form(RMSE), form(MAE)],
                            index= ["Broj ispitanika",  "R²", "F","p(F)", 'JB', 'p(JB)', "RMSE", "MAE"],
                           columns= ['Vrednosti'])    
        return data
