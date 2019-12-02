//多级表单联动
function Select(choose, id, register_url) {
    let data;
    // let csrftoken = csrf;
    let select = document.getElementById(choose);
    $(id).html("");  //每次从星选择当前列表，就亲空下一级列表框
    for (let i=0;i<select.length;i++){
        if(select[i].selected){
            Name = select[i].text;
            data = {
                "name":Name
            };
            $.ajax({          // 发起ajax请求
                url:register_url,
                // headers:{"X-CSRFToken": csrftoken }, //加上csrf验证头
                type:"POST",
                data:JSON.stringify(data),
                contentType:"application/json; charset=UTF-8",
                success:function (data) {
                    if(data){
                        $("<option value='0'></option>").appendTo(id);
                        for (let sub_cat_id in data ){
                            // 将后端返回的数据逐项插入到下一级列表框中
                            $("<option value='"+ sub_cat_id +"'>" + data[sub_cat_id] + "</option>").appendTo(id)
                        }
                    }
                    else {
                        alert('error');
                    }
                }
            });
        }
    }
}