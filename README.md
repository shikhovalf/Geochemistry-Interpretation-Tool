
#Geochemical Interpretation Tool

#Description 

This Streamlit app allows geologists and geochemists to visualize, analyze, and interpret geochemical data from sediment cores. Users can upload Excel files containing elemental data and explore geochemical ratios, facies classifications and depositional environment interpretations interactively.

#Features

- Upload Excel Data: Supports elemental geochemistry files with columns like Ca, Mg, Ti, Mn, Fe, Sr, Ba, K, Na, V, Cr, and Depth (elemnatal ratio shuld be in the same  ).  
- *Geochemical Ratio Tracks:* Interactive plots for major ratios like V/Cr, Fe/Mn, Sr/Ba, Na/K, Ca/Mg, Ti/Mn, and (Na+K)/(Ca+Mg).  
- Facies Classification: Automatically classifies Redox conditions, Salinity, Weathering intensity, Sediment type, and Depositional Environment.  
- Interactive Exploration: Select depth intervals and explore individual ratio tracks interactively with hover information.  
- Statistical Interpretation Summary: For the selected depth interval, the app calculates:
  - Dominant Redox condition and percentage breakdown of other conditions  
  - Dominant Salinity  
  - Weathering intensity  
  - Dominant Sediment type  
  - Depositional Environment  

#Use Cases

- Chemostratigraphy  
- Paleoenvironmental interpretation  
- Core or outcrop geochemical visualization  

#Usage

1. Upload your Excel file via the sidebar.  
2. Select a Depth Interval using the slider to focus on specific sections.  
3. Explore Overall Geochemical Ratios: Interactive Plotly plots show multiple ratios together for comparison.  
4. Explore Individual Ratios: Each ratio has its own interactive plot with hover tooltips.  
5. Check Statistical Interpretation Summary: Automatically generated summary shows the dominant geochemical and sedimentary conditions within the selected depth interval.

#Use Cases

- Chemostratigraphy
- Paleoenvironmental interpretation
- Core or outcrop geochemical visualization

#Installation

1. Clone the repository:
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>


#References for geochemical interpretations 

Algeo, T.J. & Lyons, T.W. (2006). Mo–U covariation in modern anoxic marine environments: Implications for analysis of paleoredox and paleohydrographic conditions. Paleoceanography, 21, PA1016.

Algeo, T.J. & Liu, J. (2020). A re-evaluation of elemental proxies for paleoredox analysis. Chemical Geology, 540, 119549.

Bathurst, R.G.C. (1975). Carbonate Sediments and Their Diagenesis. Elsevier, Amsterdam.

Calvert, S.E. & Pedersen, T.F. (1993). Geochemistry of recent oxic and anoxic marine sediments: Implications for the geological record. Marine Geology, 113, 67–88.

Cox, R., Lowe, D.R. & Cullers, R.L. (1995). The influence of sediment recycling and basement composition on evolution of mudrock chemistry in the southwestern United States. Sedimentary Geology, 95, 213–234.

Engel, A.S. & Lyons, T.W. (2003). Trace element geochemistry of sediments in sulfidic environments. Geochimica et Cosmochimica Acta, 67, 297–312.

Jones, B. & Manning, D.A.C. (1994). Comparison of geochemical indices used for the interpretation of palaeoredox conditions in ancient mudstones. Chemical Geology, 111, 111–129.

Machel, H.G. (2004). Concepts and models of dolomitization: A critical reappraisal. Earth-Science Reviews, 65, 215–273.

Morford, J.L. & Emerson, S. (1999). The geochemistry of redox sensitive trace metals in sediments. Geochimica et Cosmochimica Acta, 63, 1735–1750.

Nesbitt, H.W. & Young, G.M. (1982). Early Proterozoic climates and plate motions inferred from major element chemistry of lutites. Nature, 299, 715–717.

Nesbitt, H.W. & Young, G.M. (1984). Prediction of some weathering trends of plutonic and volcanic rocks based on thermodynamic and kinetic considerations. Geochimica et Cosmochimica Acta, 48, 1523–1534.

Roser, B.P. & Korsch, R.J. (1988). Provenance signatures of sandstone–mudstone suites determined using discriminant function analysis of major-element data. Geological Society of America Bulletin, 100, 212–222.

Shikhova, L.F. & Efendiyeva, E.N. (2019). Miocene deposits of the western part of the Absheron archipelago: lithologic-mineralogical, geochemical, geophysical and microfaunistic investigations. Proceedings of Voronezh State University. Series: Geology, №4, p.47-56

Tribovillard, N., Algeo, T.J., Lyons, T. & Riboulleau, A. (2006). Trace metals as paleoredox and paleoproductivity proxies: An update. Chemical Geology, 232, 12–32.

Tucker, M.E. (2001). Sedimentary Petrology: An Introduction to the Origin of Sedimentary Rocks. Blackwell Science, Oxford.

Tucker, M.E. & Wright, V.P. (1990). Carbonate Sedimentology. Blackwell Scientific Publications, Oxford.

Wei, W. & Algeo, T.J. (2020). Elemental proxies for paleosalinity analysis of ancient sedimentary systems. Palaeogeography, Palaeoclimatology, Palaeoecology, 540, 109531.

Wignall, P.B. & Myers, K.J. (1988). Interpreting benthic oxygen levels in mudrocks: A new approach. Geology, 16, 452–455.
