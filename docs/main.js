function init(counts) {
    let relative_chart = undefined;

    function is_showall() {
        let url = window.location.search;
        let hash = url.slice(1).split('&');
        for(let i=0;i<hash.length;i++){
            if (hash[i].indexOf('showall') == 0) {
                return true;
            }
        }
        return false;
    }
    let showall = is_showall();
    let last_update = new Date(counts['last_update']);
    let title = showall ? '全都道府県' : '累計感染者数上位10都道府県';
    title = title + 'を対象とした、感染者数の時系列表示。';
    if (!showall) {
        title += '全都道府県版は<a href="./?showall">こちら</a>'
    }
    title += '<p>最終更新日時: ' + last_update + '</p>';
    document.getElementById('abstract').innerHTML = title;


    function init_threshold() {
        let input = document.getElementById('threshold');
        input.value = 2;
        input.onchange = function() {
            draw_relative_date();
        }
    }
    init_threshold();

    function calc_relative_date(threshold) {
        let org_data = counts['original_date'];
        let locations = counts['prefectures'];
        let relative_data = {};
        locations.forEach(function(e) {
            if (org_data[e]) {
                let cum_data = org_data[e]['cumulative'];
                for(let i=0;i<cum_data.length;i++) {
                    if (cum_data[i] >= threshold) {
                        relative_data[e] = cum_data.slice(i);
                        break;
                    }
                }
            }
        })
        return relative_data;
    }

    function draw_relative_date() {
        let ctx = document.getElementById('relative_date').getContext('2d');
        let locations = counts['prefectures'];
        let datasets = [];
        let max = 0;
        let labels = [];
        let threshold = document.getElementById('threshold').value;
        let relative_data = calc_relative_date(threshold);
        let target = showall ? locations :counts['top10'];
        target.forEach(function(v){
            let data = relative_data[v];
            if (data) {
                if (data.length > max) {
                    max = data.length;
                }
                datasets.push(
                {
                    label: v,
                    data: data,
                    fill: false,
                    backgroundColor: counts['colors'][v],
                    // hidden: data[data.length-1] > SHOWING_THRESHOLD ? false : true,
                    lineTension: 0
                });
            }
        })
        for (let i=0;i<max;i++) {
            labels.push(i);
        }
        if (relative_chart) {
            relative_chart.destroy();
        }

        relative_chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {}
        });

    }

    function draw_original_date() {
        let ctx = document.getElementById('original_date').getContext('2d');
        let locations = counts['prefectures'];
        let datasets = [];
        let target = showall ? locations :counts['top10'];
        target.forEach(function(v){
            let data = counts['original_date'][v];
            if (data) {
                let cum_data = data['cumulative'];
                datasets.push(
                {
                    label: v,
                    backgroundColor: counts['colors'][v],
                    data: cum_data,
                    fill: false,
                    lineTension: 0
                });
            }
        })
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: counts['date'].map(e => e.substring(0,10)),
                datasets: datasets
            },
            options: {}
        });
    }

    draw_relative_date();
    draw_original_date();
}


fetch('./count_by_location.json').then(response => response.json()).then(init);
