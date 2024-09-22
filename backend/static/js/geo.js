//function changeRegion(region) {
//    return { type: 'CHANGE_REGION', region };
//}
//
//function changeCity(city) {
//    return { type: 'CHANGE_CITY', city };
//}

function onGeoOk(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    axios.get(`https://dapi.kakao.com/v2/local/geo/coord2address.json?x=${lon}&y=${lat}&input_coord=WGS84`
        , { headers: { Authorization: `` } }
    )
        .then(res => {
            const addressName = res.data.documents[0].address.address_name;
            console.log(res.data.documents)
            console.log(addressName)
            //changeRegion(res.data.documents[0].address.region_1depth_name)
            //changeCity(res.data.documents[0].address.region_2depth_name)
            input = document.getElementById('address')
            input.value = addressName
        }
        ).catch(e => console.log(e))
}

function onGeoError() {
    alert("위치권한을 확인해주세요");
}

//navigator.geolocation.getCurrentPosition(위치받는함수, 에러났을때 함수)
navigator.geolocation.getCurrentPosition(onGeoOk, onGeoError)