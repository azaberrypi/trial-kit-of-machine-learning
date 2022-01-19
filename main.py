from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import time
import requests
import codecs
import os
import tensor_test
from googletrans import Translator

client = WebClient(token=os.environ['Slack_Bot_token'])     # replace your own OAuth Token
channel_id = os.environ['Slack_temp_channel_ID']    # replace specific Channel ID yourself
admin_user_id = os.environ['Slack_aza_ID']  # replace specific User ID yourself
command_for_shutdown = "shutdown"   # rewrite as you like

rotation_time = 10.0

# the notification of program booted to Slack
client.chat_postMessage(
    channel=channel_id,
    text="画像を受け付けを開始しました。",
)

try:
    while 1:
        # retrieve conversation histories and process date
        result_conversations_history = client.conversations_history(channel=channel_id)
        conversation_history = result_conversations_history["messages"]
        conversation_history_json = json.dumps(conversation_history, indent=2)  # class 'str'
        conversation_history_dictionary = json.loads(conversation_history_json)

        # shutdown process by command.
        if(conversation_history_dictionary[0]['text'] == command_for_shutdown and conversation_history_dictionary[0]['user'] == admin_user_id):
            print("received command for shut down")

            # the notification of shutdown to Slack
            result2 = client.chat_postMessage(
                channel=channel_id,
                text="プログラムをシャットダウンします。",
            )
            exit()


        for i in range(5):
            if(float(conversation_history_dictionary[i]['ts']) + rotation_time > time.time()):   # react only the time difference between the current time and uploaded time is within rotation time[sec]
                #if(conversation_history_dictionary[i]['user'] != <bot_ID>):  # for prohibiting to react to bot's moving
                try:
                    #print(conversation_history_dictionary[i]["files"][0]["url_private_download"]) # for debug

                    content = requests.get(
                        conversation_history_dictionary[i]["files"][0]["url_private_download"],
                        allow_redirects=True,  # track redirects
                        headers={'Authorization': 'Bearer %s' % os.environ['Slack_Bot_token']},
                        stream=True
                    ).content

                    user_id = conversation_history_dictionary[i]["files"][0]["user"]
                    thread_id = conversation_history_dictionary[i]["ts"]

                    image_pass = "./input.jpg"  # replace file pass yourself

                    target_file = codecs.open(image_pass, "wb")
                    target_file.write(content)  # REVIEW: type(content) is not fit completely?
                    target_file.close()

                    # the notification of receiving an image from user.
                    result = client.chat_postMessage(
                        channel=channel_id,
                        text="画像を受け付けました。:love_letter:",
                        thread_ts=thread_id,
                        reply_broadcast=True,
                    )

                    # processing of machine learning
                    prediction_result = tensor_test.vgg(image_pass, tensor_test.model)      # <class 'list'>
                    #print(prediction_result[0][1])     # debug

                    # send image to channel (not used this time)
                    """
                    result_file_upload = client.files_upload(
                        channels=channel_id,
                        initial_comment="nya",
                        file=<path>,      # specify file (e.g. processed image)
                    )
                    """

                    # translate
                    translator = Translator()
                    trans_1 = translator.translate(str(prediction_result[0][1]), src="en", dest='ja')
                    trans_2 = translator.translate(str(prediction_result[1][1]), src="en", dest='ja')
                    trans_3 = translator.translate(str(prediction_result[2][1]), src="en", dest='ja')


                    result1 = client.chat_postMessage(
                        channel=channel_id,
                        # for mention
                        text="<@" + user_id + "> \n"\
                              + str(prediction_result[0][1]) + "[" + trans_1.text + "]\n" \
                              + str(prediction_result[1][1]) + "[" + trans_2.text + "]\n" \
                              + str(prediction_result[2][1]) + "[" + trans_3.text + "]\n",
                        )

                    break   # to process only the newest image

                except:
                    print("There is nothing of images.")

        #print("complete.")     # debug
        time.sleep(rotation_time-2.0)   # rewrite as you like while taking the processing time into consideration

except KeyboardInterrupt:
    print("Shut down because \"Ctrl + C\" is pressed.")

    # the notification of program shut down to Slack
    result2 = client.chat_postMessage(
        channel=channel_id,
        text="プログラムをシャットダウンします。",
    )
    del tensor_test.model
    exit()
