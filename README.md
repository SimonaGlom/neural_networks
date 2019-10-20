# Klasifikácia zvieracích zvukov

__Autori:__ Dominik Jurečko & Simona Glombíková  

## Motivácia

Zvuky sú prirodzenou súčasťou života každého z nás. Náš mozog dokáže vnímať zvuky nepretržite a následne ich spracovať. Spracovaním vznikne potrebná informácia. Zachytené poznatky mám zvyšujú kvalitu života a dotváraju ďalší senzor možnosti poznania. Práve pomocou sluchu môžeme detekovať, že nemôžeme prejsť cez cestu, vypočuť si kamaráta alebo spríjemniť si cestovanie obľúbenou hudbou.

Detekcia zvierat na základe počutia je začiatočným krokom pri učení detí rozpoznávať zvieratá, avšak len málo z nás sa nad zvieracími zvukmi zamyslí aj inak. A to pohľadu komunikácie. Veľryby sa vzhľadom na nedostatok viditeľnosti v moriach a nedostatočnému zraku dorozumievajú zvukmi, echolokáciou. Vďaka nej môžu detekovať nebezpečenstvo alebo iného jedinca v okolí. Keďže v našej oblasti veľrybu asi ťažko uvidíme, predstavme si domácich maznáčikov. Zvuk ktoréhokoľvek z nich môže pre nás predstavovať pomoc z hľadiska bezpečnosti, či predpovedania prírodných katastrof.

Identifikácia druhu zvierat je prirodzený spôsob kontroly životného prostredia a posudzovania biodiverzity. Preto je dôležitosť klasifikovanie druhu zvieraťa po vypočutí zvukovej vzorky veľmi dôležitá.

## Hypotéza

S akou pravdepodobnosťou sa zvierací zvuk identifikuje k triedam hľadaných zvierat?

## Podobné práce

Skúmanie zvuku má v dnešnom svete vzostupný charakter. V podobných prácach sme narazili na generalizáciu tohto problému bez ohľadu na domény. Zvukový súbor (napríklad vo formáte .wav) pomocou predspracovaní a extrahovania vstúpi do výpočtu ako spektogram alebo MFCC spektogram. 
> Hlavný rozdiel spočíva v tom, že spektrogram používa lineárnu frekvenčnú stupnicu. Zatiaľ čo MFCC spektogram používa logaritmickú frekvenčnú stupnicu, ktorá je podobnejšia ľudskému zvukovému vnímaniu. 

Prístup klasifikácie z predspracovaných dát sa delil na 2 množiny. 
 1. Skrytý Markov Model (ďalej HMM) - po predspracovaných dátach je potrebná ešte vektorová kvantizácia. Tento model je známy svojou použiteľnosťou na poli rozpoznávania časových vzorov, teda je použiteľný aj na náš problém. Základný vzor je Markov model, od ktorého je HMM odvodené práve kvôli skrytiu stavu. Avšak výstup viditeľný je. [3][4]
 2. Konvolučné neurónové siete (ďalej CNN) - siahajú až do 80. rokov, ale len nedávno boli prijaté ako metóda výberu pre rôzne úlohy klasifikácie objektov. V prácach sa líšil počet použitých vrstiev konvolučných sietí. Boli použité 2 [2] - 3 [1] vrstvy s maximálnym združovaním a dropdown-om. Aktivácia pri vrstvách bola vykonávaná pomocou funkcie ReLU.

## Dataset

Použitiu neurónových sietí na klasifikačné úlohy predchádza proces ich trénovania. Počas tohto procesu neurónová sieť, extrahovaním hlbšieho významu z poskytnutých dát, získavá požadovanú schopnosť zaradiť objekt do vybraných tried. Trénovanie neurónovej siete priamo závisí na samotnom návrhu a implementácii neurónovej siete, ako aj na kvalite a kvantite dát poskytnutých na jej učenie.

Dáta potrebné na trénovanie a následne overenie funkčnosti neurónovej siete je možné získať z niekoľkých zdrojov, z ktorých dostupné sú:
1. Extrakcia zvukov zvierat z video súborov (napr. videá z youtube)
2. Použitie amatérskych datasetov a zvukových súborov (zvukové banky)
3. Použitie verejných zvukových archívov zozbieraných vedeckými inštitúciami

Pri zohľadnení kvality, vierohodnosti (nie je možné manuálne overiť každý zvukový súbor) a robustnosti dostupných zdrojov, je posledný spomínaný zdroj (verejné zvukové archívy) najvhodnejším z nich.

Voľne dostupné zvukové archívy, ktoré poskytujú požadované dáta:
1. [Zvukový archív zvierat Prírodovedného múzea v Berlíne](https://www.gbif.org/dataset/b7ec1bf8-819b-11e2-bad2-00145eb45e9a)
2. [Zvuková knižnica Macaulay](https://www.macaulaylibrary.org)

Tieto datasety spoločne poskytujú viac ako stotisíc zvukových nahrávok rôznych druhov zvierat. Nájdeme v nich kratšie aj dlhšie zvukové nahrávky (od dvoch sekúnd, až po niekoľko minút). Okrem zvukových nahrávok a dát o nich, datasety poskytujú aj základné informácie (identifikátor, meno, ...) o zvierati prislúchajúcom k zvukovej stope. Tieto dáta je následne možné jednoducho rožšíriť pomocou ľahko dostupných informácií o vybranom zvierati, čo môže pomôcť k vyššej presnosti klasifikácie (napr. odlíšenie zvukov párnokopytníkov a vtákov podľa príslušnosti k zvieraciemu radu).

## Návrh riešenia na vysokej úrovni

Vstup do klasifikácie zvieracích zvukov je surový súbor obsahujúci krátke audio jedného zvieracieho zvuku (napr. štekajúci pes). 

__Predspracovanie__ - Zvukové vlny sa digitalizujú vzorkovaním v diskrétnych intervaloch - vzorkovacia frekvencia. Každá vzorka je amplitúda vlny v konkrétnom časovom intervale. Bitová hĺbka určuje podrobnosť vzorky a jej dynamického rozsahu signálu. Následne takto vytvorenú dátovú množinu znormalizujeme.

__MFCC__ - Ďalším krokom algoritmu je zo normalizovaných dát vyextrahovať vlastnosti, ktoré budeme pri trénovaní dát používať. Rozhodli sme sa použiť MFCC spektogram kvôli spomínanej podobnosti s ľudským vnímaním zvuku.

__CNN__ - Na začiatku sa budeme držať prístupu zo sekcie podobných prác [2] a [1], ktorý sme predstavili vyššie. Následne sa pokúsime iteráciou dosiahnuť, čo najlepšie výsledky. 

Tabuľka zobrazujúca výstup na obrázku znázorňuje s akou pravdepodobnosťou zvuk zvieraťa na vstupe patrí do druhu zvieraťa/triedy zvieraťa. Zvuková stopa (zvuk zvieraťa) je klasifikovaná do triedy s najvyššou pravdepodonosťou správnej predikcie.

![Algoritmus navrhu riesenia projektu](./images/algo.png)

## Citácie

[1] J. Salamon and J. P. Bello, "Deep Convolutional Neural Networks and Data Augmentation for Environmental Sound Classification," in IEEE Signal Processing Letters, vol. 24, no. 3, pp. 279-283, March 2017.

[2] K. J. Piczak, "Environmental sound classification with convolutional neural networks," 2015 IEEE 25th International Workshop on Machine Learning for Signal Processing (MLSP), Boston, MA, 2015, pp. 1-6.

[3] Vacher, Michel & Serignat, Jean-François & Chaillol, Stéphane. (2007). Sound Classification in a Smart Room Environment: an Approach using GMM and HMM Methods

[4] Balemarthy, Siddhardha & Sajjanhar, Atul & Zheng, Xi. (2018). Our Practice Of Using Machine Learning To Recognize Species By Voice. 
