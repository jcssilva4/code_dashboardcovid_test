# List of packages for session
.packages = c("tidyverse","lubridate","sf","biscale","magrittr","rvest","readxl",
               "maps","ggiraph","RColorBrewer","leaflet","plotly","geojsonio","cowplot",
               "flexdashboard","tibbletime","leaflet.extras","EpiEstim","pals","htmltools",
              "XML","plyr","htmlwidgets")

# Install CRAN packages (if not already installed)
.inst <- .packages %in% installed.packages()
if(length(.packages[!.inst]) > 0) install.packages(.packages[!.inst])

# Load packages into session 
lapply(.packages, require, character.only=TRUE)


# Start building the map

# set Working Directory as the code_dashboard directory
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
setwd('..')

# read geo data
recife_bairros = read_rds("data/suplement_inputs/recife_bairros.rds")

# read the most recent epidemic DB
db_map = read_excel("data/data_repo/epidem_data_2020-08-10.xlsx")

north_arrow <- '<img src="https://image.flaticon.com/icons/svg/731/731590.svg" alt="Direction free icon" title="North Direction" width="64" height="64">'

# set pals
pal_casosAtivos <- colorNumeric(
  palette = "Spectral",
  domain = db_map$Active_cases,
  reverse = TRUE
)

pal_FOI <- colorNumeric(
  palette = "Spectral",
  domain = db_map$FOI,
  reverse = TRUE
)

# map
map5 <- db_map %>% 
  leaflet(
    options = leafletOptions(zoomControl = TRUE,
                             scrollWheelZoom = FALSE,
                             zoomSnap = 0.25, 
                             zoomDelta = 0.5,
                             dragging = TRUE),
    width = '100%',
    height = '800px')  %>%
  addLayersControl(baseGroups = c("Força da infecção", # 1
                                  'Casos ativos'), #2
                   options = layersControlOptions(collapsed = FALSE),
                   position = "topright") %>%
  addProviderTiles(providers$CartoDB.Positron) %>%
  fitBounds(-35.018515,  -8.155340, -34.857559,  -7.926497 ) %>%
  addPolygons(group = "Força da infecção",
              data = recife_bairros,
              fillColor = ~pal_FOI(db_map$FOI),
              fillOpacity = 0.5,
              stroke = TRUE,
              color = 'black',
              weight = 1,
              smoothFactor = 0.2,
              label = ~sprintf("<strong style='text-align:center;color:darkblue'> %s </strong><br/><hr>
                     <strong>Casos ativos:</strong> %s<br/>
                     <strong>Força da infecção:</strong> %.5f",
                               recife_bairros$bairro_nome,
                               format(db_map$Active_cases, decimal.mark = ",", big.mark = "."),
                               db_map$FOI) %>% 
                lapply(htmltools::HTML),
              labelOptions = labelOptions(textsize = "12px")) %>% 
  addPolygons(group = "Casos ativos",
              data = recife_bairros,
              fillColor = ~pal_casosAtivos(db_map$Active_cases),
              fillOpacity = 0.5,
              stroke = TRUE,
              color = 'black',
              weight = 1,
              smoothFactor = 0.2,
              label = ~sprintf("<strong style='text-align:center;color:darkblue'> %s </strong><br/><hr>
                     <strong>Casos ativos:</strong> %s<br/>
                     <strong>Força da infecção:</strong> %.5f",
                               recife_bairros$bairro_nome,
                               format(db_map$Active_cases, decimal.mark = ",", big.mark = "."),
                               db_map$FOI) %>% 
                lapply(htmltools::HTML),
              labelOptions = labelOptions(textsize = "12px")) %>% 
  addResetMapButton() %>%
  addFullscreenControl() %>%
  suspendScroll(sleep = FALSE) %>%
  addScaleBar(position = "bottomleft") %>%
  addControl(html = north_arrow,
               position = "bottomright",
               className = "") %>%
  htmlwidgets::onRender("
    function(el, x) {
      this.on('baselayerchange', function(e) {
        e.layer.bringToBack();
      })
    }") %>%
  addLegend(pal = pal_FOI,
            values = ~FOI,
            labFormat = labelFormat(prefix = "", suffix = "", 
                                    #between = ", ", 
                                    #transform = function(x) 100 * x
                                    big.mark = " "),
            group = "Força da infecção",
            position = "topright" ,
            title = "Força da infecção") %>%
  addLegend(pal = pal_casosAtivos,
            values = ~Active_cases,
            labFormat = labelFormat(prefix = "", suffix = "", 
                                    #between = ", ", 
                                    #transform = function(x) 100 * x
                                    big.mark = " "),
            group = "Casos ativos",
            position = "topright" ,
            title = "Casos ativos") %>%
  htmlwidgets::onRender("
      function(el, x) {
        var updateLegend = function () {
            var selectedGroup = document.querySelectorAll('input:checked')[0].nextSibling.innerText.substr(1);
  
            document.querySelectorAll('.legend').forEach(a => a.hidden=true);
            document.querySelectorAll('.legend').forEach(l => {
              if (l.children[0].children[0].innerText == selectedGroup) l.hidden=false;
            });
        };
        updateLegend();
        this.on('baselayerchange', e => updateLegend());
      }")
map5


map5 <- htmlwidgets::prependContent(
  map5,
  htmltools::tags$style(
    "
  .legend-bivar {
    padding: 2px;
    font: 10px Arial, Helvetica, sans-serif;
    background: white;
    box-shadow: none;
    border: black;
    border: 2px solid rgba(0,0,0,0.2);
    border-radius: 5px;
    background-clip: padding-box;
  }

  .legend-bivar img{
    margin: 0;
  }
  ")
)

file = "index.html"

saveWidget(map5, file = "index.html")


mapshot(map5, url = paste0(getwd(), "/index.html"))

write_xlsx(recife_bairros,"data/suplement_inputs/recife_bairros.xlsx") # couldn't write geommetry column (MULTIPOLYGON) to file


