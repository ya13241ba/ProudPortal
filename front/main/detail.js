// import axios from axios;

var rootpath = 'http://localhost:6543';
var vm = new Vue({
    el: "#app",
    data(){
        return {
            items:[],
        };
    },
    created() {
        var url = rootpath + '/api/detail' + location.search;
        axios.get(url).then(response => {
            this.items.length = 0;
            this.items.push({key:"サイト", value:response.data.site});
            this.items.push({key:"ＩＤ", value:response.data.item_id});
            this.items.push({key:"タイトル", value:response.data.title});
            this.items.push({key:"作者", value:response.data.authors});
            this.items.push({key:"コメント", value:response.data.comments});
            this.items.push({key:"サムネイル", value:response.data.cover_url});
            this.items.push({key:"タグ", value:response.data.tags});
            this.items.push({key:"ジャンル", value:response.data.gunre});
            this.items.push({key:"専売", value:response.data.monopoly});
            this.items.push({key:"発行日", value:response.data.pubdate});
            this.items.push({key:"発行者", value:response.data.publisher});
            this.items.push({key:"イベント", value:response.data.event});
        });
    },
    // methods: {
    //     search_onclick: function(event) {
    //     }
    // }
});
