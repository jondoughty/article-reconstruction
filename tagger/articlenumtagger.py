# junktagger.py
# Brandon Livitski

from tagger.basetagger import *


def tag(issue):
	"""
	Assigns article numbers and paragraph numbers to all TXT
	"""
	assert check_tags_exist(issue, ["PI", "BL", "HL", "N", "B", "AT", "TXT"])

	issue = copy.deepcopy(issue)

	# divides the issue into pages based off page number, additionally counts number of articles
	pages = []
	current_page_num = 0
	current_page = []
	num_articles = 0
	on_HL = False
	for i, row in issue.tags_df.iterrows():
		if issue.tags_df.loc[i, "page"] == 0:
			continue

		if issue.tags_df.loc[i, "function"] == "HL":
			if not on_HL:
				num_articles = num_articles + 1
			#TODO make this an int??	
			issue.tags_df.loc[i, "article"] = int(num_articles)
			on_HL = True
		else:
			on_HL = False
		if issue.tags_df.loc[i, "page"] != current_page_num:
			if current_page_num > 0:
				pages.append(current_page)
			current_page = []
			current_page_num = current_page_num + 1
		current_page.append((i, row))

	article_stubs = []
	article_chunks = []
	for page in pages:
		in_segment = False
		without_txt = 0
		stub = False
		current_segment = []
		for i, row in page:
			if not in_segment:
				current_segment = []
				if issue.tags_df.loc[i, "function"] == "HL":
					stub = True
				elif issue.tags_df.loc[i, "function"] == "TXT":
					stub = False
					current_segment.append((i, row))
				else:
					continue
				without_txt = 0
				in_segment = True
			else:
				if stub and issue.tags_df.loc[i, "function"] == "HL":
					if len(current_segment) == 0:
						continue
					else:
						if stub:
							article_stubs.append(current_segment)
						else:
							article_chunks.append(current_segment)
						stub = True
						without_txt = 0
						current_segment = []
						continue
						#new block found 
				if without_txt > 2:
					without_txt = 0
					in_segment = False
					if stub:
						article_stubs.append(current_segment)
					else:
						article_chunks.append(current_segment)
				elif issue.tags_df.loc[i, "function"] != "TXT":
					if stub and len(current_segment) == 0:
						continue
					without_txt = without_txt + 1
				else:
					current_segment.append((i, row))
					without_txt = 0
		if len(current_segment) > 0:
			if stub:
				article_stubs.append(current_segment)
			else:
				article_chunks.append(current_segment)

	stub_bags = []
	for stub in article_stubs:
		tokens = []
		for i, row in stub:
			for token in row.text.split():
				tokens.append(token)
		tokens = set(tokens)
		stub_bags.append(tokens)

	for chunk in article_chunks:
		for i, row in chunk:
			chunk_bag = set(row.text.split())
			index = stub_bags.index(max(stub_bags, key = lambda x: len(x & chunk_bag)))
			article_stubs[index].append((i, row))

	current_article_num = 1
	print(len(article_stubs))
	for article in article_stubs:
		current_paragraph_num = 1
		for i, row in article:
			issue.tags_df.loc[i, "article"] = current_article_num
			issue.tags_df.loc[i, "paragraph"] = current_paragraph_num
			current_paragraph_num = current_paragraph_num + 1
		current_article_num = current_article_num + 1

	return issue


def main():
	issues, untagged_issues = get_issues(columns=["paragraph", "article"],
	                                     tags=["PI", "BL", "HL", "N", "B", "TXT", "AT"])

	print(issues[0].tags_df)
	print(tag(untagged_issues[0]).tags_df)


if __name__ == "__main__":
   main()
