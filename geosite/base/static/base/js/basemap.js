    function GetData(map, layers) {
      // Load map data for the current map bounds
      bounds = map.getBounds()
      console.log('Bounds now:', bounds.toBBoxString())

      var parameters = {
          bbox: map.getBounds().toBBoxString()
      };
      fullUrl = 'geodata/objects/89' +L.Util.getParamString(parameters)
      console.log('aap',fullUrl)


      var request = new XMLHttpRequest();
      request.open('GET',fullUrl, true);
      request.onload = function(){
          if (request.status >= 200 && request.status < 400){
              // success
              var data = JSON.parse(request.responseText);
              console.log('Received OK!')
              //  Work with JSON data here
              layers['fields'].clearLayers()
              layers['fields'].addData(data);      
              // console.log(data.properties.name)  
          } else {
              // made connection, got error
              console.log(request.responseText)
          }
      };
      request.onerror = function () {
          console.log('Error receiving data')
      };
      request.send();
    }


    var nlMapsHolder = document.getElementById('nlmaps-holder');
    nlMapsHolder.style.height = '100%'; // Change to required height
    
    var opts = {
        style: 'grijs',
        target: 'nlmaps-holder',
        center: {
            longitude: 6.585402,
            latitude: 52.386392
        },
        overlay: 'false',
        marker: false,
        zoom: 8,
        search: true
    };
    var map = nlmaps.createMap(opts);

    layers = {'fields':L.geoJSON().addTo(map),
              'locs':L.geoJSON().addTo(map),
              'putten':L.geoJSON().addTo(map)
              }

    map.on("moveend", function () {
      GetData( map, layers )
    });

    console.log(map)
    // GetData(map,layers)

