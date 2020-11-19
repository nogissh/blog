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
        $('#article_list').append(`
            <div class="section uk-padding-small uk-background-default uk-margin-bottom">
                <p class="uk-text-right" style="margin: 0; font-size: 13px;">
                    投稿日: ${ v.formatted_created_at }
                </p>

                <h2 class="uk-text-lead uk-margin-small">
                    <a href="/articles/${ v.id }">
                        ${ v.title}
                    </a>
                </h2>

                <p>
                    ${ v.description }
                </p>

                <div class="uk-text-center">
                    <p>
                        <a href="/articles/${ v.id }">記事を読む</a>
                    </p>
                </div>
            </div>
        `);
    });
});
