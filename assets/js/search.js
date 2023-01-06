var state = {
    info: null,
    loading: false
};

$(document).ready(function () {
    $.ajax({
        url: '/static/search.json',
        dataType: 'json',
        cache: false,
        success: function (data, textStatus) {
            state.info = data;
            state.loading = true;
        },
        error: function (xhr, textStatus, errorThrown) {
            alert('error');
        }
    });
});

$('#search-button').click(function () {
    if (state.loading === false) {
        alert('データをローディング中です。');
        return;
    }

    var selectedTags = [];

    $('input[name="tag"]').each(function (i, v) {
        if (v.checked) {
            selectedTags.push(v.value);
        }
    });

    if (selectedTags.length === 0) {
        alert('タグを選択してください。');
        return;
    }

    let results = [];
    for (let i = 0; i < state.info.articles.length; i++) {
        for (let j = 0; j < selectedTags.length; j++) {
            if (state.info.articles[i].tags.includes(selectedTags[j])) {
                results.push(state.info.articles[i]);
                break;
            }
        }
    };

    $('#article_list').empty();

    results.forEach(function (v) {
        let tagElements = v.tags.map(function (t) { return `<span class="uk-label uk-margin-small-right">${ t }</span>` }).join('');

        $('#article_list').append(`
            <div class="section uk-padding-small uk-background-default uk-margin-bottom">
                <h2 class="uk-text-lead uk-margin-top">
                    <a href="/articles/${ v.id }">
                        ${ v.title}
                    </a>
                </h2>

                <p class="uk-text-small">
                    ${ v.description }
                </p>

                <div>
                    <span uk-icon="tag" class="uk-margin-small-right"></span>
                    ${ tagElements }
                </div>

                <p class="uk-text-small uk-margin-small">
                    作成日：${ v.created_date }
                </p>
            </div>
        `);
    });
});
