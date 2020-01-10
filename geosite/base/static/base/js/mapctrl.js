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

    $scope.$on('leafletDirectiveMap.myMap.zoomend', function(event){
        $scope.eventDetected = "ZoomEnd";
        $scope.update()
    });

    $scope.$on('leafletDirectiveMap.myMap.dragend', function(event){
        $scope.eventDetected = "DragEnd";
        $scope.update()
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
  		$scope.field = {'name':fld.name,'id':fld.id}
  		$scope.fieldinfo = {}
      $http.get("geodata/info/"+fld.id).success(function(data, status) {
  		    $scope.fieldinfo = data
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

    angular.extend($scope, {

        tiles: {
            url: "https://geodata.nationaalgeoregister.nl/tiles/service/wmts/brtachtergrondkaartgrijs/EPSG:3857/{z}/{x}/{y}.png"
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
                lat: 52.5,
                lng: 6,
                focus: false,
                title: "Marker",
                draggable: false,
                message: "?",
                opacity: 0
            }
        },
        fields:['all','for','now'],
        field:'No field selected',
        fieldinfo:{'no':'info'},
        count:1,
        fields_downloaded_for_bounds:undefined,
        spinnerstatus:'loading',
    });
// "loading:not"



    function newground(){
      if ($scope.fields_downloaded_for_bounds == undefined) {return true}
      return (
        $scope.bounds.southWest.lng < $scope.fields_downloaded_for_bounds.southWest.lng ||
        $scope.bounds.southWest.lat < $scope.fields_downloaded_for_bounds.southWest.lat ||
        $scope.bounds.northEast.lng > $scope.fields_downloaded_for_bounds.northEast.lng ||
        $scope.bounds.northEast.lat > $scope.fields_downloaded_for_bounds.northEast.lat )
    }

    $scope.islinkedobject = function(value){
      console.log('islinkedobject: ', value)
      if (Array.isArray(value) && value.length()==2) {
        return true;
      };
      return false;
    };

    $scope.update = function(){

      // console.log('Should I update? ',newground())
      if (newground()) {
          $scope.spinnerstatus="loading"        

          // Get the countries geojson data from a JSON
          var bb = $scope.bounds.southWest.lng + ',' + $scope.bounds.southWest.lat +
                ',' + $scope.bounds.northEast.lng+ ',' + $scope.bounds.northEast.lat
          // console.log('UPDATE FIELD LIST')
          $http.get("geodata/objects/89",{'params': {'bbox':bb}}).success(function(data, status) {
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
                  }
              });

              $scope.fields = []
              for (var item of data.features) {
                 $scope.fields.push({'name':item.properties.name,'id':item.properties.id,'latlon':item.properties.lalo})
               }

              $scope.fields_downloaded_for_bounds = $scope.bounds
          });  
          $scope.spinnerstatus="loading:not"        
      }
      else{
        // console.log('NO NEED TO UPDATE FIELD LIST') 
      }    

    }

    $scope.increase = function(input){
    	$scope.count = $scope.count + 1
    }

    $scope.clickField = function (input){
      countryClick(input,'a')
      $scope.center={lat: input.latlon[0], lng: input.latlon[1], zoom: 10}
      $scope.markers.m1.focus=true
      $scope.markers.m1.lat=input.latlon[0]
      $scope.markers.m1.lng=input.latlon[1]
      $scope.markers.m1.message=input.name
      $scope.markers.m1.opacity=1
    }

    console.log('Now go update the fields')
    $scope.update()
    console.log('Done')

} ]);
