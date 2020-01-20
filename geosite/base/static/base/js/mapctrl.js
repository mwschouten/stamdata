// mapctrl.js

var app = angular.module("demoapp", ["leaflet-directive"]);

app.controller("GeoJSONController", [ '$scope', '$http', 'leafletData','leafletMapEvents', 
function($scope, $http, leafletData,leafletMapEvents) {

    $scope.eventDetected = "No events yet...";

    $scope.$on("leafletDirectiveGeoJson.myMap.mouseover", function(ev, leafletPayload) {
        countryMouseover(leafletPayload.leafletObject.feature, leafletPayload.leafletEvent);
    });

    $scope.$on("leafletDirectiveGeoJson.myMap.click", function(ev, leafletPayload) {
        countryClick(leafletPayload.leafletObject.feature.properties, leafletPayload.leafletEvent);
    });

    $scope.$on('leafletDirectiveMap.myMap.click', function(event){
        $scope.eventDetected = "Click";
    });


    // Mouse over function, called from the Leaflet Map Events
    function countryMouseover(feature, leafletEvent) {
      var layer = leafletEvent.target;
      layer.setStyle({
          weight: 2,
          color: '#666',
          fillColor: 'white'
      });
      layer.bringToFront();
		  $scope.field = {'name':feature.properties.name,'id':feature.properties.id}
    }

    function countryClick(fld, leafletEvent) {
      $scope.info_object = {'name':fld.name,'id':fld.id}
      $scope.info = {}
      $http.get("geodata/info/"+fld.id).success(function(data, status) {
          $scope.info = data
      });
    }


    function infoClick(input, leafletEvent) {
      $scope.info_object = {'name':input[0],'id':input[1]}
      $scope.info = {}
      $http.get("geodata/info/"+[input[1]]).success(function(data, status) {
          $scope.info = data
      });
    }


    var bounds = {
        southWest: {
            lat: 51.5,
            lng: 3.0,
        },
        northEast: {
            lat: 53.5,
            lng: 8.0,
        }
    }

    var blue={
                type: 'div',
                iconSize: [5, 5],
                className: 'blue',
                iconAnchor:  [5, 5]
            }

    angular.extend($scope, {

        tiles: {
            url: "https://geodata.nationaalgeoregister.nl/tiles/service/wmts/brtachtergrondkaartgrijs/EPSG:3857/{z}/{x}/{y}.png"
        },
        layers: {
          baselayers: {
              nederland: {
                  name:'grijsnederland',
                  type:'xyz',
                  url: "https://geodata.nationaalgeoregister.nl/tiles/service/wmts/brtachtergrondkaartgrijs/EPSG:3857/{z}/{x}/{y}.png"
              },
          },
          overlays: {
              main: {
                  name:"selectie",
                  visible: true,
                  type:"group",
                  layerParams: {
                    showOnSelector: false,
                  },
              },
              lokaties: {
                  name: "mijnbouwlokaties",
                  type: "group",
                  visible: true,
                  layerOptions:{maxClusterRadius:50}
              }
          }
        },
        bounds: bounds,
        center: {},
        defaults: {
            scrollWheelZoom: true
        },
        events: {
          map: {
              enable: ['zoomend', 'dragend', 'click'],
              logic: 'emit'
          }
        },        
        markers: {
            m1: {
              layer:'main',
                lat: 52.5,
                lng: 6,
                focus: false,
                title: "Marker",
                draggable: false,
                message: "?",
                visible: true,
                opacity: 0
            },
        },
        fields:[],
        field:'No field selected',
        fieldinfo:{'no':'info'},
        count:1,
        fields_downloaded_for_bounds:undefined,
        spinnerstatus:'loading',
    });

    $scope.islinkedobject = function(value){
      console.log('islinkedobject: ', value)
      if (Array.isArray(value) && value.length()==2) {
        return true;
      };
      return false;
    };


    // var sites = {
    //         A:{layer: "lokaties", lat: 53.29109, lng: 6.74189, message: "plekA"},
    //         B:{layer: "lokaties", lat: 53.33109, lng: 6.34189, message: "plekB"},
    //         C:{layer: "lokaties", lat: 53.00109, lng: 6.44189, message: "plekC"}
    // }
    // for (var key in sites) {
    //     sites[key].icon = blue
    // }
    // $scope.markers = Object.assign($scope.flag,sites)
    // console.log('Markers : ',$scope.markers)

    $scope.update = function(){

      $http.get("geodata/locations").success(function(data, status) {
          for (const [key, value] of Object.entries(data)) {
            value.layer='lokaties'
            value.message=key
            value.icon=blue
            $scope.markers[key] = value
          }
      });

      // Get the countries geojson data from a JSON
      $http.get("geodata/fields").success(function(data, status) {
          angular.extend($scope, {
              geojson: {
                  data: data,
                  style: {
                      fillColor: "green",
                      weight: 1,
                      opacity: 0.7,
                      color: 'green',
                      dashArray: '1',
                      fillOpacity: 0.5
                  },
                  resetStyleOnMouseout: true
              },
              fields:[]
        });
        for (var item of data.features) {
           $scope.fields.push({'name':item.properties.name,'id':item.properties.id,'latlon':item.properties.lalo})
         }
      });  
    }

    $scope.clickID = function (input){
      console.log('Clicked clickID: ',input)
      $scope.info_object = {'name':input[0],'id':input[1]}
      $scope.info = {}
      $http.get("geodata/info/"+[input[1]]).success(function(data, status) {
          $scope.info = data
          $scope.center={lat: data.lalo[0], lng: data.lalo[1], zoom: 10}
          $scope.markers.m1.focus=true
          $scope.markers.m1.lat=data.lalo[0]
          $scope.markers.m1.lng=data.lalo[1]
          $scope.markers.m1.message=data.name
          $scope.markers.m1.opacity=1
      });


    }


    $scope.clickField = function (input){
      console.log('Clicked clickField: ',input)
      countryClick(input,'a')
      $scope.center={lat: input.latlon[0], lng: input.latlon[1], zoom: 10}
      $scope.markers.m1.focus=true
      $scope.markers.m1.lat=input.latlon[0]
      $scope.markers.m1.lng=input.latlon[1]
      $scope.markers.m1.message=input.name
      $scope.markers.m1.opacity=1
      console.log('Markers ',$scope.layers.overlays.main)
    }

    console.log('Now go update the fields')
    $scope.update()
    console.log('Done')

} ]);
