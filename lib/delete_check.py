import delete_everything
import settings
import sqs


def check(my_settings: settings.Settings):
    raw_message = sqs.get_messages(my_settings)

    if len(raw_message) < 1:
        print("No message on queue... so we can't report back")
        return
    messages = [sqs.parse_message(m) for m in raw_message]
    delete_messages = [
        m for m in messages if
        m.get('RequestType') == "Delete"
    ]
    if len(delete_messages) < 1:
        print("No message of type Delete")
        return

    out, err, return_code = delete_everything.delete_everything(my_settings)
    for delete_message in delete_messages:
        if return_code != 0:
            sqs.report_cr_deletion_failure(my_settings, delete_message.get('LogicalResourceId'))
        else:
            sqs.report_cr_deletion_success(my_settings, delete_message.get('LogicalResourceId'))
