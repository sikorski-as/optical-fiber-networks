Optymalizacja zasobów węzła w sieciach teleinformatycznych z wykorzystaniem algorytmów heurystycznych.  
  
twórcy: Kacper Wnuk i Arkadiusz Sikorski  
promotor: dr Stanisław Kozdrowski 

Uruchomienie projektu w środowisku Linux

1. Projekt wymaga zainstalowanego Pythona minimum w wersji 3.5, poniżej znajduje się link, w którym krok po kroku została opisana instalacja dla systemu Ubuntu i LinuxMint  
https://tecadmin.net/install-python-3-5-on-ubuntu/
2. Projekty w Pythonie warto przechowywać w wirtualnych środowiskach, może być konieczna instalacja pakietu, który to umożliwia:  
apt-get install python3-venv
3. Następnie w głównym folderze o nazwie optical_fiber_networks wykonać polecenie: source deploy.sh.
Polecenie to utworzy wirtualne środowisko do pracy.
4. Proszę ustawić zmienną środowiskową będąc cały czas w głównym folderze:  
export PYTHONPATH=. 
5. Skrypty znajdują się w folderze batchtests. Pierwszy - single.sh uruchamia raz kod z pliku batch_example.py również znajdującego się w folderze batchtests.
Drugi, uruchamia skrypt batch_example.py równolegle w tle odpowiednią ilość razy, którą można zmodyfikować w owym pliku. 
Uruchomienia skryptów należy wykonać z głównego folderu poleceniami:   
source batchtests/single.sh  
source batchtests/parallel.sh  
W pliku batch_example.py można ustawić dla jakich sieci wykonywany jest skrypt oraz dla jakich zapotrzebowań. Wszystkie dostępne możliwości zostały podane
na górze w zakomentowanej sekcji.
W celach testowych zalecane jest użycie skryptu single.sh.
Chcąc zmienić parametry poszczególnych algorytmów należy skonfigurować pliki config.py w folderach, których nazwa odnosi się do modyfikowanego algorytmu.
Np. dla algorytmu genetycznego plik config.py znajduje się w folderze genetic.
