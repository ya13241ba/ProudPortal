// import axios from axios;

var rootpath = 'http://localhost:6543';
var vm = new Vue({
    el: "#app",
    data(){
        return {
            in_site:"melon",
            in_item_id:"",
            items:[],
        };
    },
    created() {
        // var url = rootpath + '/api/detail?site=' + this.in_site + '&id=d_158233'
        // axios.get(url).then(response => {
        //     this.items.push(response.data);
        // });
    },
    methods: {
        search_onclick: function(event) {
            var url = rootpath + '/api/detail?site=' + this.in_site + '&id=' + this.in_item_id;
            axios.get(url).then(response => {
                // vue.items.push(response.data);

                this.items.push(response.data);
            });
        }
    }
});
